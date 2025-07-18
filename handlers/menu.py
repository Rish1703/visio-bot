from telegram import InlineKeyboardButton, InlineKeyboardMarkup  # ✅ импорт

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("⚡ Start", callback_data="start")],
        [InlineKeyboardButton("🖼 Generate", callback_data="generate")],
        [InlineKeyboardButton("📊 Мои генерации", callback_data="stats")],
        [InlineKeyboardButton("💳 Купить 100 изображений", callback_data="buy")],
        [InlineKeyboardButton("🧬 Анимировать фото", callback_data="animate")],
        [InlineKeyboardButton("🎨 Редактировать фото", callback_data="edit_photo")],  # ✅ новая кнопка
    ]
    return InlineKeyboardMarkup(keyboard)

