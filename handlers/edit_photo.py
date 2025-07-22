from telegram import Update
from telegram.ext import ContextTypes
from services.edit_service import edit_photo
import logging
import tempfile
import os
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

async def handle_edit_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("➡️ Получено фото или текст для редактирования")

    if not context.user_data.get("awaiting_edit"):
        return

    context.user_data["awaiting_edit"] = False

    photo = update.message.photo[-1]
    caption = update.message.caption

    if not caption:
        await update.message.reply_text("❗ Пожалуйста, добавь описание к фото (что нужно изменить).")
        return

    await update.message.reply_text("🎨 Редактирую фото по описанию...")

    try:
        # Загружаем фото из Telegram
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()

        # Конвертируем фото в PNG с альфа-каналом (RGBA)
        image = Image.open(BytesIO(photo_bytes)).convert("RGBA")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
            image.save(temp_image, format="PNG")
            temp_image_path = temp_image.name

        logger.info(f"📤 Отправка в DALL·E: prompt='{caption}', file='{temp_image_path}'")
        edited_image_url = edit_photo(temp_image_path, caption)
        logger.info(f"✅ Ответ DALL·E: {edited_image_url}")

        await update.message.reply_photo(photo=edited_image_url, caption="Готово! ✨")

    except Exception as e:
        logger.exception(f"❌ Ошибка при обращении к DALL·E: {e}")
        await update.message.reply_text(f"❌ Не удалось отредактировать фото: {e}")

    finally:
        # Удаляем временный файл, если он был создан
        if 'temp_image_path' in locals() and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
