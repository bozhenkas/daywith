from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

BTN_ADD_HABIT = "+ добавить привычку"
BTN_GOOD = "хорошая"
BTN_BAD = "плохая"
BTN_BACK = "назад"
BTN_SKIP = "пропустить"

def get_habits_list_keyboard(habits: List[dict]) -> InlineKeyboardMarkup:
    kb = []
    for h in habits:
        icon = "🟢" if h["type"] == "good" else "🔴"
        kb.append([InlineKeyboardButton(text=f"{icon} {h['name']}", callback_data=f"habit:edit:{h['_id']}")])
    kb.append([InlineKeyboardButton(text=BTN_ADD_HABIT, callback_data="habit:add")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_habit_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=BTN_GOOD, callback_data="htype:good"),
            InlineKeyboardButton(text=BTN_BAD, callback_data="htype:bad")
        ],
        [InlineKeyboardButton(text=BTN_BACK, callback_data="habit:cancel_add")]
    ])

def get_skip_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BTN_SKIP, callback_data="setup:skip")]
    ])

def get_habit_edit_keyboard(habit_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="удалить", callback_data=f"habit:del:{habit_id}")],
        [InlineKeyboardButton(text=BTN_BACK, callback_data="menu:habits")]
    ])
