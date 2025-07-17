from telegram import Update
from telegram.ext import ContextTypes
from services.supabase_service import get_user_usage, update_user_usage
from .menu import main_menu_keyboard

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_usage = await get_user_usage(user_id)
    await update_user_usage(user_id, limit=user_usage["limit"] + 100)
    await update.message.reply_text("✅ Оплата прошла успешно!")
    await update.message.reply_text("Выбери действие:", reply_markup=main_menu_keyboard())
