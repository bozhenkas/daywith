from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from bot.config.messages_loader import get_msg
from bot.keyboards.settings_kb import get_settings_keyboard, get_time_preset_keyboard
from bot.keyboards.main_menu import get_back_reply_keyboard
from bot.services.habit_service import HabitService
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(F.text == "настройки")
async def show_settings(message_or_callback, habit_service: HabitService, state: FSMContext = None):
    user_id = message_or_callback.from_user.id
    user = await habit_service.repo.db.users.find_one({"telegram_id": user_id})
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
    
    if isinstance(message_or_callback, Message):
        msg1 = await message_or_callback.answer("ℹ", reply_markup=get_back_reply_keyboard())
        msg2 = await message_or_callback.answer(text, reply_markup=get_settings_keyboard())
        if state:
            await state.update_data(menu_msg_ids=[msg1.message_id, msg2.message_id])
    else:
        await message_or_callback.message.edit_text(text, reply_markup=get_settings_keyboard())

@router.callback_query(F.data == "set:time")
async def change_time(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("Выбери новое время:", reply_markup=get_time_preset_keyboard())

@router.callback_query(F.data == "set:notif")
async def toggle_notif(callback: CallbackQuery, habit_service: HabitService):
    await callback.answer()
    new_val = await habit_service.toggle_notifications(callback.from_user.id)
    on = get_msg("settings.notifications_on")
    off = get_msg("settings.notifications_off")
    notif_str = on if new_val else off
    
    await callback.answer(get_msg("settings.notifs_updated", status=notif_str))
    await show_settings(callback, habit_service)
