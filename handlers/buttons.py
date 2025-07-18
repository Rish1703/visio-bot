from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes
from core.config import PROVIDER_TOKEN
from services.supabase_service import get_user_usage
from .menu import main_menu_keyboard
import json


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если пользователь отправил /start
    if update.message:
        await update.message.reply_text(
            text="Привет! Я — бот Visio, помогу тебе сгенерировать изображения по описанию.",
            reply_markup=main_menu_keyboard()
        )
        return

    # Если пользователь нажал на кнопку
    query = update.callback_query
    if not query:
        return
    await query.answer()

    user_id = str(query.from_user.id)
    user_usage = await get_user_usage(user_id)

    if query.data == "start":
        await query.edit_message_text("Привет! Я — бот Visio...", reply_markup=main_menu_keyboard())

    elif query.data == "generate":
        await query.edit_message_text("✨ Напиши, что ты хочешь сгенерировать — и я превращу текст в изображение!")
        context.user_data["awaiting_prompt"] = True

    elif query.data == "stats":
        remaining = max(0, user_usage["limit"] - user_usage["count"])
        await query.edit_message_text(
            text=f"📊 Твои генерации:\n✅ Осталось: {remaining} из {user_usage['limit']}",
            reply_markup=main_menu_keyboard()
        )

    elif query.data == "buy":
        prices = [LabeledPrice("100 генераций", 50000)]
        provider_data = {
            "receipt": {
                "items": [{
                    "description": "100 генераций изображений",
                    "quantity": 1,
                    "amount": {"value": 500, "currency": "RUB"},
                    "vat_code": 1,
                    "payment_mode": "full_payment",
                    "payment_subject": "commodity"
                }],
                "tax_system_code": 1
            }
        }
        await context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title="Покупка 100 изображений",
            description="Ты получишь 100 генераций изображений",
            payload="buy_100",
            provider_token=PROVIDER_TOKEN,
            currency="RUB",
            prices=prices,
            start_parameter="buy",
            need_email=True,
            send_email_to_provider=True,
            provider_data=json.dumps(provider_data)
        )

    elif query.data == "animate":
        await query.edit_message_text(
            "🧬 Пришли фото, которое хочешь оживить. Добавь подпись с текстом — я сделаю видео с анимацией и озвучкой!"
        )
        context.user_data["awaiting_animation"] = True

    elif query.data == "edit_photo":
        await query.edit_message_text(
            "🎨 Пришли фото, которое хочешь отредактировать.\n\nНапример:\n— Добавь очки\n— Удали задний фон\n— Сделай рождественский стиль\n— Добавь радугу на фоне\n\n📸 Просто отправь картинку с описанием — и я сделаю магию!"
        )
        context.user_data["awaiting_inpainting_photo"] = True

