# bot.py

import os
import sys
import asyncio

# На Windows до импорта telegram ставим правильный policy
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
import openai
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import openai

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8443))

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь команду /generate и введи описание картинки.")

# Обработка команды /generate
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Что ты хочешь сгенерировать? Напиши описание:")

    return 1  # Переход к состоянию ожидания текста

# Получение промпта и генерация изображения через DALL·E 3
async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    user_id = update.effective_user.id

    await update.message.reply_text("Генерирую изображение, подожди 10-15 секунд...")

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
    except Exception as e:
        logging.error(f"Ошибка генерации: {e}")
        await update.message.reply_text("Ошибка при генерации изображения. Попробуй позже.")

    return -1  # Завершить диалог

# Основной запуск
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    from telegram.ext import ConversationHandler

    conversation = ConversationHandler(
        entry_points=[CommandHandler("generate", generate)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt)]},
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversation)

    # Для Railway: webhook
    app.run_polling()


if __name__ == "__main__":
    main()

