from aiogram.types import InlineKeyboardButton
import json

try:
    btn = InlineKeyboardButton(**{"text": "Test", "callback_data": "btn", "style": "success", "icon_custom_emoji_id": "123"})
    print("Success:", btn.model_dump())
except Exception as e:
    print("Error:", e)
