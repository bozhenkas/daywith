from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_time_preset_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="09:00", callback_data="time:09:00"),
            InlineKeyboardButton(text="21:00", callback_data="time:21:00"),
            InlineKeyboardButton(text="22:00", callback_data="time:22:00")
        ],
        [InlineKeyboardButton(text="ввести вручную ✎", callback_data="setup:time_manual")]
    ])


def get_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="изменить время ⏰", callback_data="set:time")],
        [InlineKeyboardButton(text="вкл/выкл уведомления 🔔", callback_data="set:notif")],
        [InlineKeyboardButton(text="часовой пояс 🌍", callback_data="set:tz")]
    ])
