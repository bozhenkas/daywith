from aiogram import Router, F
from aiogram.types import CallbackQuery
from config.messages_loader import get_msg
from keyboards.settings_kb import get_settings_keyboard, get_time_preset_keyboard
from services.habit_service import HabitService

router = Router()

@router.callback_query(F.data == "menu:settings")
async def show_settings(callback: CallbackQuery, habit_service: HabitService):
    user = await habit_service.repo.db.users.find_one({"telegram_id": callback.from_user.id})
    if not user:
        return
        
    on = get_msg("settings.notifications_on")
    off = get_msg("settings.notifications_off")
    notif_str = on if user.get("notifications_enabled", True) else off
    
    text = get_msg(
        "settings.menu", 
        time=user.get("digest_time", "21:00"),
        notify=notif_str,
        lang=user.get("language", "ru"),
        tz=user.get("timezone", "UTC")
    )
    
    await callback.message.edit_text(text, reply_markup=get_settings_keyboard())

@router.callback_query(F.data == "set:time")
async def change_time(callback: CallbackQuery):
    await callback.message.edit_text("Выбери новое время:", reply_markup=get_time_preset_keyboard())

@router.callback_query(F.data == "set:notif")
async def toggle_notif(callback: CallbackQuery, habit_service: HabitService):
    new_val = await habit_service.toggle_notifications(callback.from_user.id)
    on = get_msg("settings.notifications_on")
    off = get_msg("settings.notifications_off")
    notif_str = on if new_val else off
    
    await callback.answer(get_msg("settings.notifs_updated", status=notif_str))
    await show_settings(callback, habit_service)
