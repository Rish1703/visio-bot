from telegram import Update
from telegram.ext import ContextTypes
from services.edit_service import edit_photo
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

async def handle_edit_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_edit"):
        return

    context.user_data["awaiting_edit"] = False

    photo = update.message.photo[-1]
    caption = update.message.caption

    if not caption:
        await update.message.reply_text("❗ Пожалуйста, добавь описание к фото (что нужно изменить).")
        return

    await update.message.reply_text("🎨 Фото и описание получены.\n⏳ Начинаю редактирование, подожди пару секунд...")

    try:
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()

        # Временный PNG-файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
            temp_image.write(photo_bytes)
            temp_image_path = temp_image.name

        logger.info(f"📸 Фото сохранено во временный файл: {temp_image_path}")
        logger.info(f"📄 Описание: {caption}")

        edited_image_url = edit_photo(temp_image_path, caption)

        logger.info(f"✅ Получен URL от DALL·E: {edited_image_url}")

        await update.message.reply_photo(photo=edited_image_url, caption="✨ Готово! Вот твоё отредактированное фото.")

        os.remove(temp_image_path)

    except Exception as e:
        logger.error(f"❌ Ошибка при редактировании: {e}")
        await update.message.reply_text(f"❌ Ошибка при редактировании: {e}")
