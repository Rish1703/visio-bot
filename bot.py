import os
import sys
import asyncio
import logging
import json
from dotenv import load_dotenv
import openai
from supabase import create_client, Client

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    PreCheckoutQueryHandler,
    filters,
)
from fastapi import FastAPI, Request

# --------------------- Windows Event Loop Fix ---------------------
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# --------------------- Load ENV ---------------------
load_dotenv()
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN")

openai.api_key = OPENAI_API_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
FREE_LIMIT = 5

logging.basicConfig(level=logging.INFO)

# --------------------- SUPABASE ---------------------
async def get_user_usage(user_id):
    data = supabase.table("usage").select("*").eq("user_id", user_id).execute().data
    if data:
        return data[0]
    else:
        supabase.table("usage").insert({
            "user_id": user_id,
            "count": 0,
            "limit": FREE_LIMIT
        }).execute()
        return {"user_id": user_id, "count": 0, "limit": FREE_LIMIT}

async def update_user_usage(user_id, count=None, limit=None):
    updates = {}
    if count is not None:
        updates["count"] = count
    if limit is not None:
        updates["limit"] = limit
    supabase.table("usage").update(updates).eq("user_id", user_id).execute()

# --------------------- UI ---------------------
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Start", callback_data="start")],
        [InlineKeyboardButton("🖼 Generate", callback_data="generate")],
        [InlineKeyboardButton("📊 Мои генерации", callback_data="stats")],
        [InlineKeyboardButton("💳 Купить 100 изображений", callback_data="buy")]
    ])

# --------------------- Handlers ---------------------
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query:
        await query.answer()
        user_id = str(query.from_user.id)
        user_usage = await get_user_usage(user_id)

        if query.data == "start":
            await query.edit_message_text(
                text="Привет! Я — бот Visio, помогу тебе сгенерировать изображения по описанию.",
                reply_markup=main_menu_keyboard()
            )
        elif query.data == "generate":
            await query.edit_message_text("Что ты хочешь сгенерировать? Напиши описание:")
            context.user_data["awaiting_prompt"] = True
        elif query.data == "stats":
            remaining = max(0, user_usage["limit"] - user_usage["count"])
            await query.edit_message_text(
                text=f"📊 Твои генерации:\n✅ Осталось: {remaining} из {user_usage['limit']}",
                reply_markup=main_menu_keyboard()
            )
        elif query.data == "buy":
            prices = [LabeledPrice("100 генераций", 50000)]
            provider_data = {
                "receipt": {
                    "items": [
                        {
                            "description": "100 генераций изображений",
                            "quantity": 1,
                            "amount": {
                                "value": 500,
                                "currency": "RUB"
                            },
                            "vat_code": 1,
                            "payment_mode": "full_payment",
                            "payment_subject": "commodity"
                        }
                    ],
                    "tax_system_code": 1
                }
            }

            await context.bot.send_invoice(
                chat_id=query.message.chat_id,
                title="Покупка 100 изображений",
                description="Ты получишь 100 генераций изображений",
                payload="buy_100",
                provider_token=PROVIDER_TOKEN,
                currency="RUB",
                prices=prices,
                start_parameter="buy",
                need_email=True,
                send_email_to_provider=True,
                provider_data=json.dumps(provider_data)
            )
    else:
        await update.message.reply_text(
            "Привет! Я — бот Visio, помогу тебе сгенерировать изображения по описанию.",
            reply_markup=main_menu_keyboard()
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_prompt"):
        return
    context.user_data["awaiting_prompt"] = False
    user_id = str(update.effective_user.id)
    prompt = update.message.text
    user_usage = await get_user_usage(user_id)

    if user_usage["count"] >= user_usage["limit"]:
        await update.message.reply_text(
            "❗ Ты использовал все генерации.\n💳 Хочешь продолжить? Оплати 500₽ за 100 генераций.",
            reply_markup=main_menu_keyboard()
        )
        return

    await update.message.reply_text("🧠 Генерирую изображение, подожди...")
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard",
        )
        image_url = response.data[0].url
        await update.message.reply_photo(photo=image_url, caption="Готово!")
        await update_user_usage(user_id, count=user_usage["count"] + 1)
    except Exception as e:
        logging.error(f"Ошибка генерации: {e}")
        await update.message.reply_text("❌ Ошибка. Попробуй позже.")
    await update.message.reply_text("Выбери следующее действие:", reply_markup=main_menu_keyboard())

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_usage = await get_user_usage(user_id)
    await update_user_usage(user_id, limit=user_usage["limit"] + 100)
    await update.message.reply_text("✅ Оплата прошла успешно! Лимит увеличен на 100 изображений.")
    await update.message.reply_text("Выбери действие:", reply_markup=main_menu_keyboard())

# --------------------- FastAPI ---------------------
app = FastAPI()
bot_app = Application.builder().token(TOKEN).build()

bot_app.add_handler(CallbackQueryHandler(handle_buttons))
bot_app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
bot_app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
bot_app.add_handler(MessageHandler(filters.COMMAND & filters.Regex("^/start$"), handle_buttons))

@app.on_event("lifespan")
async def lifespan(app: FastAPI):
    await bot_app.initialize()
    await bot_app.start()
    yield
    await bot_app.stop()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=8000)



