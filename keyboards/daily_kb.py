from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

BTN_DONE = "✓"
BTN_NOT_DONE = "✗"

def get_daily_check_keyboard(habits: List[dict]) -> InlineKeyboardMarkup:
    keyboard = []
    for habit in habits:
        row = [
            InlineKeyboardButton(
                text=f"{habit['name']} {BTN_DONE}",
                callback_data=f"daily:done:{habit['_id']}",
                **{"style": "success"} if True else {}
            ),
            InlineKeyboardButton(
                text=f"{BTN_NOT_DONE}",
                callback_data=f"daily:skip:{habit['_id']}",
                **{"style": "danger"} if True else {}
            )
        ]
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
