from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

def get_date_navigation_keyboard(current_date: datetime) -> InlineKeyboardMarkup:
    prev_date = current_date - timedelta(days=1)
    next_date = current_date + timedelta(days=1)
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀", callback_data=f"hist:prev:{prev_date.strftime('%Y-%m-%d')}"),
            InlineKeyboardButton(text=current_date.strftime("%d.%m.%Y"), callback_data="hist:noop"),
            InlineKeyboardButton(text="▶", callback_data=f"hist:next:{next_date.strftime('%Y-%m-%d')}")
        ],
        [
            InlineKeyboardButton(text="выбрать дату", callback_data="hist:pick"),
            InlineKeyboardButton(text="сегодня", callback_data="hist:today")
        ]
    ])
