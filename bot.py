# bot.py

import os
import sys
import asyncio
import logging

from dotenv import load_dotenv
import openai

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Настройка событийного цикла на Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Константа состояния
GENERATE_DESCRIPTION = 1

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь команду /generate и введи описание картинки.")

# Команда /generate
async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Что ты хочешь сгенерировать? Напиши описание:")
    return GENERATE_DESCRIPTION

# Обработка текста-подсказки
async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text

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

    return ConversationHandler.END

# Команда отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

# Основной запуск
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчик диалога
    conversation = ConversationHandler(
        entry_points=[CommandHandler("generate", generate)],
        states={
            GENERATE_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversation)

    # Запуск в режиме polling
    app.run_polling()

if __name__ == "__main__":
    main()


