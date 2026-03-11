from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_onboarding_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="перейти в меню →", callback_data="menu:main")],
        [InlineKeyboardButton(text="поменять время уведомления ⏰", callback_data="set:time")],
        [InlineKeyboardButton(text="сбросить всё ✗", callback_data="setup:reset_confirm")]
    ])


def get_reset_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="да, сбросить", callback_data="setup:reset_yes"),
            InlineKeyboardButton(text="нет", callback_data="menu:main")
        ]
    ])
