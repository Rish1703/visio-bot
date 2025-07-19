from telegram import Update
from telegram.ext import ContextTypes
from services.edit_service import edit_photo
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

async def handle_edit_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если пришло фото — сохраняем, ждём описание
    if update.message.photo:
        context.user_data["last_photo"] = update.message.photo[-1]
        context.user_data["awaiting_edit"] = True
        await update.message.reply_text("🖼 Фото получено! Теперь отправь описание, что нужно изменить.")
        return

    # Если пришёл текст после фото — обрабатываем
    if context.user_data.get("awaiting_edit") and "last_photo" in context.user_data:
        context.user_data["awaiting_edit"] = False
        photo = context.user_data.pop("last_photo")
        prompt = update.message.text

        await update.message.reply_text("🎨 Редактирую фото по описанию...")

        try:
            file = await context.bot.get_file(photo.file_id)
            photo_bytes = await file.download_as_bytearray()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
                temp_image.write(photo_bytes)
                temp_image_path = temp_image.name

            edited_image_url = edit_photo(temp_image_path, prompt)

            await update.message.reply_photo(photo=edited_image_url, caption="Готово!")
            os.remove(temp_image_path)

        except Exception as e:
            logger.error(f"Ошибка редактирования: {e}")
            await update.message.reply_text(f"❌ Ошибка при редактировании фото: {e}")
    else:
        # Если пользователь ничего не отправлял ранее
        await update.message.reply_text("📸 Сначала отправь фото, затем текст с описанием.")
