import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.config.messages_loader import get_msg
from bot.keyboards.settings_kb import get_settings_keyboard, get_time_preset_keyboard
from bot.keyboards.main_menu import get_back_reply_keyboard
from bot.services.habit_service import HabitService
from bot.fsm.states import OnboardingStates, SettingsStates

logger = logging.getLogger(__name__)
router = Router()

TIMEZONE_PRESETS = [
    ("🇷🇺 Москва (UTC+3)", "Europe/Moscow"),
    ("🇺🇦 Киев (UTC+2/3)", "Europe/Kiev"),
    ("🇩🇪 Берлин (UTC+1/2)", "Europe/Berlin"),
    ("🇬🇧 Лондон (UTC+0/1)", "Europe/London"),
    ("🇰🇿 Алматы (UTC+5)", "Asia/Almaty"),
    ("🇺🇿 Ташкент (UTC+5)", "Asia/Tashkent"),
]


@router.message(F.text == "настройки")
async def show_settings(message: Message, habit_service: HabitService, state: FSMContext = None):
    user = await habit_service.get_user(message.from_user.id)
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
        tz=user.get("timezone", "Europe/Moscow"),
    )
    msg1 = await message.answer(get_msg("habits.info_emoji"), reply_markup=get_back_reply_keyboard(), disable_notification=True)
    msg2 = await message.answer(text, reply_markup=get_settings_keyboard())
    if state:
        await state.update_data(menu_msg_ids=[msg1.message_id, msg2.message_id])


@router.callback_query(F.data == "set:time")
async def change_time(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        get_msg("start.restart_onboarding"), reply_markup=get_time_preset_keyboard()
    )
    await state.set_state(OnboardingStates.waiting_for_time)


@router.callback_query(F.data == "set:notif")
async def toggle_notif(callback: CallbackQuery, habit_service: HabitService):
    await callback.answer()
    new_val = await habit_service.toggle_notifications(callback.from_user.id)
    on = get_msg("settings.notifications_on")
    off = get_msg("settings.notifications_off")
    notif_str = on if new_val else off
    await callback.answer(get_msg("settings.notifs_updated", status=notif_str), show_alert=True)

    user = await habit_service.get_user(callback.from_user.id)
    on_full = get_msg("settings.notifications_on")
    off_full = get_msg("settings.notifications_off")
    text = get_msg(
        "settings.menu",
        time=user.get("digest_time", "21:00"),
        notify=on_full if user.get("notifications_enabled", True) else off_full,
        lang=user.get("language", "ru"),
        tz=user.get("timezone", "Europe/Moscow"),
    )
    await callback.message.edit_text(text, reply_markup=get_settings_keyboard())


@router.callback_query(F.data == "set:tz")
async def choose_timezone(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data=f"tz:{tz}")]
        for label, tz in TIMEZONE_PRESETS
    ] + [[InlineKeyboardButton(text="← назад", callback_data="settings:back")]])
    await callback.message.edit_text(get_msg("settings.tz_prompt"), reply_markup=kb)
    await state.set_state(SettingsStates.waiting_for_tz)


@router.callback_query(SettingsStates.waiting_for_tz, F.data.startswith("tz:"))
async def set_timezone(callback: CallbackQuery, state: FSMContext, habit_service: HabitService):
    await callback.answer()
    tz = callback.data.split(":", 1)[1]
    await habit_service.update_user_timezone(callback.from_user.id, tz)
    await state.clear()
    await callback.message.edit_text(get_msg("settings.tz_updated", tz=tz), reply_markup=get_settings_keyboard())


@router.callback_query(F.data == "settings:back")
async def settings_back(callback: CallbackQuery, state: FSMContext, habit_service: HabitService):
    await callback.answer()
    await state.clear()
    user = await habit_service.get_user(callback.from_user.id)
    on = get_msg("settings.notifications_on")
    off = get_msg("settings.notifications_off")
    text = get_msg(
        "settings.menu",
        time=user.get("digest_time", "21:00"),
        notify=on if user.get("notifications_enabled", True) else off,
        lang=user.get("language", "ru"),
        tz=user.get("timezone", "Europe/Moscow"),
    )
    await callback.message.edit_text(text, reply_markup=get_settings_keyboard())
