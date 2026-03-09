from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

BTN_ADD_HABIT = "+ добавить привычку"
BTN_GOOD = "хорошая"
BTN_BAD = "плохая"
BTN_BACK = "назад"
BTN_SKIP = "пропустить"

def get_habits_list_keyboard(habits: List[Dict[str, Any]], page: int = 1, page_size: int = 6) -> InlineKeyboardMarkup:
    kb = []
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_habits = habits[start_idx:end_idx]
    
    for h in page_habits:
        style = "success" if h["type"] == "good" else "danger"
        kb.append([InlineKeyboardButton(text=f"{h['name']}", callback_data=f"habit:edit:{h['_id']}", **{"style": style})])
        
    total_pages = (len(habits) + page_size - 1) // page_size if habits else 1
    if total_pages > 1:
        nav_row = []
        if page > 1:
            nav_row.append(InlineKeyboardButton(text="⤝", callback_data=f"habit:page:{page - 1}", **{"style": "primary"}))
        
        nav_row.append(InlineKeyboardButton(text=f"[{page}/{total_pages}]", callback_data="habit:noop", **{"style": "primary"}))
        
        if page < total_pages:
            nav_row.append(InlineKeyboardButton(text="⤞", callback_data=f"habit:page:{page + 1}", **{"style": "primary"}))
            
        kb.append(nav_row)

    kb.append([InlineKeyboardButton(text=BTN_ADD_HABIT, callback_data="habit:add", **{"style": "primary"})])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_habit_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=BTN_GOOD, callback_data="htype:good", **{"style": "success"}),
            InlineKeyboardButton(text=BTN_BAD, callback_data="htype:bad", **{"style": "danger"})
        ],
        [InlineKeyboardButton(text=BTN_BACK, callback_data="habit:cancel_add", **{"style": "primary"})]
    ])

def get_skip_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BTN_SKIP, callback_data="setup:skip")]
    ])

def get_habit_edit_keyboard(habit_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="удалить", callback_data=f"habit:del:{habit_id}", **{"style": "danger"})],
        [InlineKeyboardButton(text=BTN_BACK, callback_data="menu:habits", **{"style": "primary"})]
    ])
