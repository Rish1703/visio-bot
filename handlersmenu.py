from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Start", callback_data="start")],
        [InlineKeyboardButton("🖼 Generate", callback_data="generate")],
        [InlineKeyboardButton("📊 Мои генерации", callback_data="stats")],
        [InlineKeyboardButton("💳 Купить 100 изображений", callback_data="buy")]
    ])
