from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BTN_TIME_09 = "09:00"
BTN_TIME_21 = "21:00"
BTN_TIME_22 = "22:00"

def get_time_preset_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=BTN_TIME_09, callback_data="time:09:00", **{"style": "primary"}),
            InlineKeyboardButton(text=BTN_TIME_21, callback_data="time:21:00", **{"style": "primary"}),
            InlineKeyboardButton(text=BTN_TIME_22, callback_data="time:22:00", **{"style": "primary"})
        ]
    ])

def get_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="изменить время", callback_data="set:time")],
        [InlineKeyboardButton(text="вкл/выкл уведомления", callback_data="set:notif")]
    ])
