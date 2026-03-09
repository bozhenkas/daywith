from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BTN_MY_HABITS = "📋 Мои привычки"
BTN_STATS = "📊 Статистика"
BTN_HISTORY = "📅 История"
BTN_SETTINGS = "⚙️ Настройки"

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BTN_MY_HABITS, callback_data="menu:habits")],
        [
            InlineKeyboardButton(text=BTN_STATS, callback_data="menu:stats"),
            InlineKeyboardButton(text=BTN_HISTORY, callback_data="menu:history")
        ],
        [InlineKeyboardButton(text=BTN_SETTINGS, callback_data="menu:settings")]
    ])
