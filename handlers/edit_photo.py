from telegram import Update
from telegram.ext import ContextTypes
from services.edit_service import edit_photo
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

# Храним путь к последнему фото
TEMP_PHOTO_KEY = "edit_temp_photo"

async def handle_edit_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 📷 Сначала пришло фото
    if update.message.photo:
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        photo_bytes = await file.download_as_bytearray()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
            temp_image.write(photo_bytes)
            context.user_data[TEMP_PHOTO_KEY] = temp_image.name

        await update.message.reply_text("✏ Теперь пришли описание, что изменить на фото.")
        return

    # 📝 Потом пришёл текст
    if update.message.text and TEMP_PHOTO_KEY in context.user_data:
        prompt = update.message.text
        temp_image_path = context.user_data.pop(TEMP_PHOTO_KEY)

        await update.message.reply_text("🎨 Редактирую фото...")

        try:
            edited_image_url = edit_photo(temp_image_path, prompt)
            await update.message.reply_photo(photo=edited_image_url, caption="Готово!")
        except Exception as e:
            logger.error(f"Ошибка редактирования: {e}")
            await update.message.reply_text(f"❌ Ошибка: {e}")
        finally:
            os.remove(temp_image_path)
        return

    # Если ни фото, ни текст
    await update.message.reply_text("❗ Сначала пришли фото, потом описание.")
