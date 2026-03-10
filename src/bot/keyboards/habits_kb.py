from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def get_habits_list_keyboard(habits: List[Dict[str, Any]], page: int = 1, page_size: int = 6) -> InlineKeyboardMarkup:
    kb = []

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_habits = habits[start_idx:end_idx]

    for h in page_habits:
        style = "success" if h["type"] == "good" else "danger"
        kb.append([InlineKeyboardButton(text=h['name'], callback_data=f"habit:edit:{h['_id']}", **{"style": style})])

    total_pages = (len(habits) + page_size - 1) // page_size if habits else 1
    if total_pages > 1:
        nav_row = []
        if page > 1:
            nav_row.append(InlineKeyboardButton(text="⤝", callback_data=f"habit:page:{page - 1}", **{"style": "primary"}))

        nav_row.append(InlineKeyboardButton(text=f"[{page}/{total_pages}]", callback_data="habit:noop", **{"style": "primary"}))

        if page < total_pages:
            nav_row.append(InlineKeyboardButton(text="⤞", callback_data=f"habit:page:{page + 1}", **{"style": "primary"}))

        kb.append(nav_row)

    kb.append([InlineKeyboardButton(text="+ добавить привычку", callback_data="habit:add", **{"style": "primary"})])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_habit_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="хорошая ✓", callback_data="htype:good", **{"style": "success"}),
            InlineKeyboardButton(text="плохая ✗", callback_data="htype:bad", **{"style": "danger"})
        ],
        [InlineKeyboardButton(text="назад", callback_data="habit:cancel_add", **{"style": "primary"})]
    ])


def get_habit_goal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1", callback_data="hgoal:1", **{"style": "primary"}),
            InlineKeyboardButton(text="2", callback_data="hgoal:2", **{"style": "primary"}),
            InlineKeyboardButton(text="3", callback_data="hgoal:3", **{"style": "primary"}),
            InlineKeyboardButton(text="4", callback_data="hgoal:4", **{"style": "primary"}),
        ],
        [
            InlineKeyboardButton(text="5", callback_data="hgoal:5", **{"style": "primary"}),
            InlineKeyboardButton(text="6", callback_data="hgoal:6", **{"style": "primary"}),
            InlineKeyboardButton(text="7", callback_data="hgoal:7", **{"style": "primary"}),
        ],
        [InlineKeyboardButton(text="назад", callback_data="habit:cancel_add", **{"style": "primary"})]
    ])


def get_skip_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="пропустить", callback_data="setup:skip", **{"style": "primary"})]
    ])


def get_habit_edit_keyboard(habit_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="переименовать ✎", callback_data=f"habit:rename:{habit_id}", **{"style": "primary"})],
        [InlineKeyboardButton(text="удалить ✗", callback_data=f"habit:del:{habit_id}", **{"style": "danger"})],
        [InlineKeyboardButton(text="← назад", callback_data="menu:habits", **{"style": "primary"})]
    ])
