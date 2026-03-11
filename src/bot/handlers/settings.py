import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.config.messages_loader import get_msg
from bot.keyboards.settings_kb import get_settings_keyboard, get_time_preset_keyboard, get_timezone_keyboard
from bot.keyboards.main_menu import get_back_reply_keyboard
from bot.services.habit_service import HabitService
from bot.fsm.states import OnboardingStates, SettingsStates
from bot.utils.timezones import UTC_OFFSET_NAMES

logger = logging.getLogger(__name__)
router = Router()

TIMEZONE_PRESETS = [
    ("Калининград (UTC+2)", "Europe/Kaliningrad"),
    ("Москва (UTC+3)", "Europe/Moscow"),
    ("Самара (UTC+4)", "Europe/Samara"),
    ("Екатеринбург (UTC+5)", "Asia/Yekaterinburg"),
    ("Омск (UTC+6)", "Asia/Omsk"),
    ("Барнаул (UTC+7)", "Asia/Barnaul"),
    ("Иркутск (UTC+8)", "Asia/Irkutsk"),
    ("Якутск (UTC+9)", "Asia/Yakutsk"),
    ("Владивосток (UTC+10)", "Asia/Vladivostok"),
    ("Магадан (UTC+11)", "Asia/Magadan"),
    ("Камчатка (UTC+12)", "Asia/Kamchatka"),
]


def _settings_text(user: dict) -> str:
    notif = get_msg(f"settings.notifications_{'on' if user.get('notifications_enabled', True) else 'off'}")
    return get_msg(
        "settings.menu",
        time=user.get("digest_time", "21:00"),
        notify=notif,
        lang=user.get("language", "ru"),
        tz=user.get("timezone", "Europe/Moscow"),
    )


@router.message(F.text == "настройки")
async def show_settings(message: Message, habit_service: HabitService, state: FSMContext = None) -> None:
    user = await habit_service.get_user(message.from_user.id)
    if not user:
        return
    msg1 = await message.answer(get_msg("habits.info_emoji"), reply_markup=get_back_reply_keyboard(), disable_notification=True)
    msg2 = await message.answer(_settings_text(user), reply_markup=get_settings_keyboard())
    if state:
        await state.update_data(menu_msg_ids=[msg1.message_id, msg2.message_id])


@router.callback_query(F.data == "set:time")
async def change_time(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.edit_text(
        get_msg("start.restart_onboarding"), reply_markup=get_time_preset_keyboard(show_back=True)
    )
    await state.set_state(OnboardingStates.waiting_for_time)


@router.callback_query(F.data == "set:notif")
async def toggle_notif(callback: CallbackQuery, habit_service: HabitService) -> None:
    new_val = await habit_service.toggle_notifications(callback.from_user.id)
    notif_str = get_msg("settings.notifications_on") if new_val else get_msg("settings.notifications_off")
    await callback.answer(get_msg("settings.notifs_updated", status=notif_str), show_alert=True)
    user = await habit_service.get_user(callback.from_user.id)
    await callback.message.edit_text(_settings_text(user), reply_markup=get_settings_keyboard())


@router.callback_query(F.data == "set:tz")
async def choose_timezone(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.edit_text(get_msg("settings.tz_prompt"), reply_markup=get_timezone_keyboard(TIMEZONE_PRESETS))
    await state.set_state(SettingsStates.waiting_for_tz)


@router.callback_query(SettingsStates.waiting_for_tz, F.data.startswith("tz:"))
async def set_timezone(callback: CallbackQuery, state: FSMContext, habit_service: HabitService) -> None:
    await callback.answer()
    tz = callback.data.split(":", 1)[1]
    if tz == "manual":
        await callback.message.edit_text(get_msg("settings.tz_manual_prompt"))
        await state.set_state(SettingsStates.waiting_for_tz_manual)
        return
    display = next((label for label, z in TIMEZONE_PRESETS if z == tz), tz)
    await habit_service.update_user_timezone(callback.from_user.id, tz)
    await state.clear()
    await callback.message.edit_text(get_msg("settings.tz_updated", tz=display), reply_markup=get_settings_keyboard())


@router.callback_query(F.data == "tz:manual")
async def tz_manual_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.edit_text(get_msg("settings.tz_manual_prompt"))
    await state.set_state(SettingsStates.waiting_for_tz_manual)


@router.message(SettingsStates.waiting_for_tz_manual)
async def process_tz_manual(message: Message, state: FSMContext, habit_service: HabitService) -> None:
    text = message.text.strip().replace("UTC", "").replace("utc", "").replace("+", "").strip() if message.text else ""
    if text not in UTC_OFFSET_NAMES:
        await message.answer(get_msg("settings.tz_manual_invalid"))
        return
    display_name, iana_tz = UTC_OFFSET_NAMES[text]
    await habit_service.update_user_timezone(message.from_user.id, iana_tz)
    await state.clear()
    await message.answer(get_msg("settings.tz_updated", tz=display_name))


@router.callback_query(F.data == "settings:back")
async def settings_back(callback: CallbackQuery, state: FSMContext, habit_service: HabitService) -> None:
    await callback.answer()
    await state.clear()
    user = await habit_service.get_user(callback.from_user.id)
    await callback.message.edit_text(_settings_text(user), reply_markup=get_settings_keyboard())
