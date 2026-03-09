from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="мои привычки")],
            [
                KeyboardButton(text="статистика"),
                KeyboardButton(text="история")
            ],
            [KeyboardButton(text="настройки")]
        ],
        resize_keyboard=True
    )

def get_back_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="назад ↵")]],
        resize_keyboard=True
    )
