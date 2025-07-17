from telegram import Update
from telegram.ext import ContextTypes
from services.did_service import animate_photo

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, ждали ли анимацию
    if not context.user_data.get("awaiting_animation"):
        return  # Если нет — выходим
    
    context.user_data["awaiting_animation"] = False  # сброс флага

    photo = update.message.photo[-1]  # самое большое фото
    text = update.message.caption or "Привет!"
    
    await update.message.reply_text("🌀 Создаю анимацию...")

    try:
        file = await context.bot.get_file(photo.file_id)
        photo_url = file.file_path

        video_url = animate_photo(photo_url, text)
        await update.message.reply_video(video=video_url, caption="Готово!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

