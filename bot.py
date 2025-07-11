import os
import sys
import asyncio
import logging
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
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    PreCheckoutQueryHandler,
    filters,
)

# Fix event loop on Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN")

openai.api_key = OPENAI_API_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(level=logging.INFO)
FREE_LIMIT = 5

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

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Start", callback_data="start")],
        [InlineKeyboardButton("🖼 Generate", callback_data="generate")],
        [InlineKeyboardButton("📊 Мои генерации", callback_data="stats")],
        [InlineKeyboardButton("💳 Купить 100 изображений", callback_data="buy")]
    ])

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
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
        await context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title="Покупка 100 изображений",
            description="Ты получишь 100 генераций изображений",
            payload="buy_100",
            provider_token=PROVIDER_TOKEN,
            currency="RUB",
            prices=prices,
            start_parameter="buy"
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Выбери действие ниже:", reply_markup=main_menu_keyboard())

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_usage = await get_user_usage(user_id)
    await update_user_usage(user_id, limit=user_usage["limit"] + 100)
    await update.message.reply_text("✅ Оплата прошла успешно! Лимит увеличен на 100 изображений.")
    await update.message.reply_text("Выбери действие:", reply_markup=main_menu_keyboard())

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex("^/start$"), start))
    app.run_polling()

if __name__ == "__main__":
    main()


