import sys
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    filters
)
from contextlib import asynccontextmanager

from core.config import TOKEN, OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY, PROVIDER_TOKEN, FREE_LIMIT
from handlers.buttons import handle_buttons
from handlers.text import handle_text
from handlers.payment import precheckout_callback, successful_payment_callback

# Windows fix
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Telegram Application
bot_app = Application.builder().token(TOKEN).build()

# Handlers
bot_app.add_handler(CommandHandler("start", handle_buttons))  # ✅ фикс
bot_app.add_handler(CallbackQueryHandler(handle_buttons))
bot_app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
bot_app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# FastAPI Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot_app.initialize()
    await bot_app.start()
    yield
    await bot_app.stop()

# FastAPI app
app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("📩 Получен update от Telegram:", data)
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

# Local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=8000)


