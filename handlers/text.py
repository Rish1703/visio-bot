from telegram import Update
from telegram.ext import ContextTypes
from services.supabase_service import get_user_usage, update_user_usage
from services.openai_service import generate_image
from .menu import main_menu_keyboard
import logging

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_prompt"):
        return
    context.user_data["awaiting_prompt"] = False

    user_id = str(update.effective_user.id)
    prompt = update.message.text
    user_usage = await get_user_usage(user_id)

    if user_usage["count"] >= user_usage["limit"]:
        await update.message.reply_text(
            "❗ Ты использовал все генерации.\n💳 Оплати 500₽ за 100 генераций.",
            reply_markup=main_menu_keyboard()
        )
        return

    await update.message.reply_text("🧠 Генерирую изображение...")
    try:
        image_url = await generate_image(prompt)
        await update.message.reply_photo(photo=image_url)
        await update_user_usage(user_id, count=user_usage["count"] + 1)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await update.message.reply_text("❌ Ошибка. Попробуй позже.")
    await update.message.reply_text("Выбери действие:", reply_markup=main_menu_keyboard())
