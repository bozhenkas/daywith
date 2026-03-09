from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BTN_MY_HABITS = "мои привычки"
BTN_STATS = "статистика"
BTN_HISTORY = "история"
BTN_SETTINGS = "настройки"

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_MY_HABITS)],
            [
                KeyboardButton(text=BTN_STATS),
                KeyboardButton(text=BTN_HISTORY)
            ],
            [KeyboardButton(text=BTN_SETTINGS)]
        ],
        resize_keyboard=True
    )

def get_back_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="назад ↵")]],
        resize_keyboard=True
    )
