from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Tuple


def get_time_preset_keyboard(show_back: bool = False) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="09:00", callback_data="time:09:00"),
            InlineKeyboardButton(text="21:00", callback_data="time:21:00"),
            InlineKeyboardButton(text="22:00", callback_data="time:22:00")
        ],
        [InlineKeyboardButton(text="ввести вручную ✎", callback_data="setup:time_manual")]
    ]
    if show_back:
        kb.append([InlineKeyboardButton(text="← назад", callback_data="settings:back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="изменить время ⏰", callback_data="set:time")],
        [InlineKeyboardButton(text="вкл/выкл уведомления 🔔", callback_data="set:notif")],
        [InlineKeyboardButton(text="часовой пояс 🌍", callback_data="set:tz")],
        [InlineKeyboardButton(text="← меню", callback_data="menu:main")]
    ])


def get_timezone_keyboard(presets: List[Tuple[str, str]]) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text=label, callback_data=f"tz:{tz}")]
        for label, tz in presets
    ]
    kb.append([InlineKeyboardButton(text="ввести UTC вручную ✎", callback_data="tz:manual")])
    kb.append([InlineKeyboardButton(text="← назад", callback_data="settings:back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)
