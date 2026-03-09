from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_onboarding_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="перейти в меню", callback_data="menu:main", **{"style": "success"})],
        [InlineKeyboardButton(text="поменять время уведомления", callback_data="set:time", **{"style": "primary"})],
        [InlineKeyboardButton(text="сбросить всё", callback_data="setup:reset_confirm", **{"style": "danger"})]
    ])

def get_reset_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="да", callback_data="setup:reset_yes", **{"style": "danger"}),
            InlineKeyboardButton(text="нет", callback_data="menu:main", **{"style": "primary"})
        ]
    ])
