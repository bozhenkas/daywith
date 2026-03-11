from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def get_habits_list_keyboard(habits: List[Dict[str, Any]], page: int = 1, page_size: int = 6) -> InlineKeyboardMarkup:
    kb = []

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_habits = habits[start_idx:end_idx]

    for h in page_habits:
        kb.append([InlineKeyboardButton(text=h['name'], callback_data=f"habit:edit:{h['_id']}")])

    total_pages = (len(habits) + page_size - 1) // page_size if habits else 1
    if total_pages > 1:
        nav_row = []
        if page > 1:
            nav_row.append(InlineKeyboardButton(text="⤝", callback_data=f"habit:page:{page - 1}"))
        nav_row.append(InlineKeyboardButton(text=f"[{page}/{total_pages}]", callback_data="habit:noop"))
        if page < total_pages:
            nav_row.append(InlineKeyboardButton(text="⤞", callback_data=f"habit:page:{page + 1}"))
        kb.append(nav_row)

    kb.append([InlineKeyboardButton(text="+ добавить привычку", callback_data="habit:add")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_habit_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="хорошая ✓", callback_data="htype:good"),
            InlineKeyboardButton(text="плохая ✗", callback_data="htype:bad")
        ],
        [InlineKeyboardButton(text="назад", callback_data="habit:cancel_add")]
    ])


def get_habit_goal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1", callback_data="hgoal:1"),
            InlineKeyboardButton(text="2", callback_data="hgoal:2"),
            InlineKeyboardButton(text="3", callback_data="hgoal:3"),
            InlineKeyboardButton(text="4", callback_data="hgoal:4"),
        ],
        [
            InlineKeyboardButton(text="5", callback_data="hgoal:5"),
            InlineKeyboardButton(text="6", callback_data="hgoal:6"),
            InlineKeyboardButton(text="7", callback_data="hgoal:7"),
        ],
        [InlineKeyboardButton(text="назад", callback_data="habit:cancel_add")]
    ])


def get_cancel_add_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="отмена ✗", callback_data="habit:cancel_add")]
    ])


def get_skip_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="пропустить", callback_data="setup:skip")]
    ])


def get_habit_edit_keyboard(habit_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="переименовать ✎", callback_data=f"habit:rename:{habit_id}")],
        [InlineKeyboardButton(text="удалить ✗", callback_data=f"habit:del:{habit_id}")],
        [InlineKeyboardButton(text="← назад", callback_data="menu:habits")]
    ])
