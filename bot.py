import sys
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, PreCheckoutQueryHandler, filters
from contextlib import asynccontextmanager
from core.config import TOKEN
from handlers.buttons import handle_buttons
from handlers.text import handle_text
from handlers.payment import precheckout_callback, successful_payment_callback

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

bot_app = Application.builder().token(TOKEN).build()
bot_app.add_handler(CallbackQueryHandler(handle_buttons))
bot_app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
bot_app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
bot_app.add_handler(MessageHandler(filters.COMMAND & filters.Regex("^/start$"), handle_buttons))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot_app.initialize()
    await bot_app.start()
    yield
    await bot_app.stop()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}


