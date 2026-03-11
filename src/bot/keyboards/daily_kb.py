from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from math import ceil

PAGE_SIZE = 7


def get_daily_check_keyboard(habits: List[dict], page: int = 1) -> InlineKeyboardMarkup:
    """3 кнопки на привычку: ✓ | название | ✗. Пагинация если > PAGE_SIZE."""
    total_pages = ceil(len(habits) / PAGE_SIZE) if habits else 1
    start = (page - 1) * PAGE_SIZE
    page_habits = habits[start:start + PAGE_SIZE]

    kb = []
    for h in page_habits:
        h_id = str(h["_id"])
        kb.append([
            InlineKeyboardButton(text="✓", callback_data=f"daily:done:{h_id}"),
            InlineKeyboardButton(text=h["name"], callback_data=f"daily:info:{h_id}"),
            InlineKeyboardButton(text="✗", callback_data=f"daily:skip:{h_id}"),
        ])

    if total_pages > 1:
        nav = []
        if page > 1:
            nav.append(InlineKeyboardButton(text="⤝", callback_data=f"daily:page:{page - 1}"))
        nav.append(InlineKeyboardButton(text=f"[{page}/{total_pages}]", callback_data="daily:noop"))
        if page < total_pages:
            nav.append(InlineKeyboardButton(text="⤞", callback_data=f"daily:page:{page + 1}"))
        kb.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=kb)
