import os
import sys
import asyncio
import logging
import json

from dotenv import load_dotenv
import openai

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Windows policy
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load env
load_dotenv()
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Состояния
GENERATE_DESCRIPTION = 1
USAGE_FILE = "usage.json"

# Загрузка лимитов
def load_usage():
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_usage(usage):
    with open(USAGE_FILE, "w") as f:
        json.dump(usage, f)

# Кнопки
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Start", callback_data="start")],
        [InlineKeyboardButton("🖼 Generate", callback_data="generate")],
        [InlineKeyboardButton("💳 Купить 100 изображений", callback_data="buy")]
    ])

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Выбери действие ниже:", reply_markup=main_menu_keyboard())

# Обработка кнопок
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        await query.edit_message_text("Привет! Я помогу тебе сгенерировать изображение.")
    elif query.data == "generate":
        await query.edit_message_text("Что ты хочешь сгенерировать? Напиши описание:")
        context.user_data["awaiting_prompt"] = True
    elif query.data == "buy":
        await query.edit_message_text("💳 Оплата пока недоступна. Функция скоро появится.")

# /generate
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Что ты хочешь сгенерировать? Напиши описание:")
    return GENERATE_DESCRIPTION

# Обработка текста
async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    prompt = update.message.text

    usage = load_usage()
    user_usage = usage.get(user_id, {"count": 0, "limit": 5})

    if user_usage["count"] >= user_usage["limit"]:
        await update.message.reply_text(
            "❗ Ты использовал все 5 бесплатных генераций.\n"
            "💳 Хочешь продолжить? Оплати 500₽ за 100 генераций."
        )
        return -1

    await update.message.reply_text("🧠 Генерирую изображение, подожди 10–15 секунд...")

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

        user_usage["count"] += 1
        usage[user_id] = user_usage
        save_usage(usage)

    except Exception as e:
        logging.error(f"Ошибка генерации: {e}")
        await update.message.reply_text("Ошибка при генерации. Попробуй позже.")

    return -1

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

# /reset <user_id>
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = 7819868423  # Замени на свой Telegram ID
    if update.effective_user.id != admin_id:
        await update.message.reply_text("⛔ У тебя нет прав.")
        return

    if not context.args:
        await update.message.reply_text("❗ Укажи ID пользователя: /reset <user_id>")
        return

    target_id = context.args[0]
    usage = load_usage()

    if target_id in usage:
        usage[target_id]["count"] = 0
        save_usage(usage)
        await update.message.reply_text(f"✅ Сброшен лимит для {target_id}")
    else:
        await update.message.reply_text("Пользователь не найден.")

# Запуск
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[CommandHandler("generate", generate)],
        states={GENERATE_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(conversation)

    app.run_polling()

if __name__ == "__main__":
    main()


