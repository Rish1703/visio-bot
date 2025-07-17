from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 Я — бот Visio. Вот что я умею:\n"
        "/start — Главное меню\n"
        "/help — Помощь\n"
        "/reset — Отменить ввод описания\n\n"
        "Чтобы создать изображение, выбери '🖼 Generate' и напиши описание!"
    )

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_prompt"] = False
    await update.message.reply_text("🔄 Ожидание ввода отменено.")
