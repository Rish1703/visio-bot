import sys
import asyncio
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    filters,
)
from contextlib import asynccontextmanager

from core.config import TOKEN
from handlers.buttons import handle_buttons
from handlers.text import handle_text
from handlers.payment import precheckout_callback, successful_payment_callback
from handlers.commands import help_command, reset_command
from handlers.animate import handle_photo  # ✅ обработчик анимации фото

# -------------------- Настройка логирования --------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------- Windows event loop fix --------------------
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# -------------------- Инициализация Telegram Bot --------------------
bot_app = Application.builder().token(TOKEN).build()

# -------------------- Подключение обработчиков --------------------
bot_app.add_handler(CommandHandler("start", handle_buttons))
bot_app.add_handler(CommandHandler("help", help_command))
bot_app.add_handler(CommandHandler("reset", reset_command))

bot_app.add_handler(CallbackQueryHandler(handle_buttons))
bot_app.add_handler(PreCheckoutQueryHandler(precheckout_callback))

bot_app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
bot_app.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_photo))  # ✅ фильтр по фото

# -------------------- FastAPI Lifespan --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot_app.initialize()
    await bot_app.start()
    logger.info("🤖 Telegram bot запущен")
    yield
    await bot_app.stop()

# -------------------- FastAPI app --------------------
app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    logger.info(f"📩 Получен update от Telegram: {data}")
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

# -------------------- Локальный запуск --------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=8000)



