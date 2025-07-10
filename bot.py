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
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Windows: event loop fix
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Загрузка .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Лимиты
USAGE_FILE = "usage.json"
FREE_LIMIT = 5

def load_usage():
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_usage(usage):
    with open(USAGE_FILE, "w") as f:
        json.dump(usage, f)

# Кнопки меню
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Start", callback_data="start")],
        [InlineKeyboardButton("🖼 Generate", callback_data="generate")],
        [InlineKeyboardButton("📊 Мои генерации", callback_data="stats")],
        [InlineKeyboardButton("💳 Купить 100 изображений", callback_data="buy")]
    ])

# Обработка нажатий кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    usage = load_usage()
    user_usage = usage.get(user_id, {"count": 0, "limit": FREE_LIMIT})

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
        await query.edit_message_text(
            text="💳 Оплата пока недоступна. Функция скоро появится.",
            reply_markup=main_menu_keyboard()
        )

# Получение текста (если ждём описание)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_prompt"):
        return

    context.user_data["awaiting_prompt"] = False
    user_id = str(update.effective_user.id)
    prompt = update.message.text

    usage = load_usage()
    user_usage = usage.get(user_id, {"count": 0, "limit": FREE_LIMIT})

    if user_usage["count"] >= user_usage["limit"]:
        await update.message.reply_text(
            "❗ Ты использовал все 5 бесплатных генераций.\n"
            "💳 Хочешь продолжить? Оплати 500₽ за 100 генераций.",
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

        user_usage["count"] += 1
        usage[user_id] = user_usage
        save_usage(usage)

    except Exception as e:
        logging.error(f"Ошибка генерации: {e}")
        await update.message.reply_text("❌ Ошибка при генерации. Попробуй позже.")

    await update.message.reply_text("Выбери следующее действие:", reply_markup=main_menu_keyboard())

# Запуск
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()

