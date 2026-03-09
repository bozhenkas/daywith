from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.config.messages_loader import get_msg
from bot.keyboards.main_menu import get_main_menu_keyboard
from bot.keyboards.settings_kb import get_time_preset_keyboard
from bot.keyboards.habits_kb import get_skip_keyboard
from bot.fsm.states import OnboardingStates
from bot.services.habit_service import HabitService
from bot.keyboards.onboarding_kb import get_onboarding_choice_keyboard, get_reset_confirm_keyboard
from aiogram import Bot

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, habit_service: HabitService):
    user = await habit_service.get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        last_name=message.from_user.last_name,
        lang_code=message.from_user.language_code,
        is_premium=message.from_user.is_premium
    )
    
    # Check if user already has a digest time set (onboarding complete)
    if user.get("digest_time") and user.get("digest_time") != "21:00": # Using 21:00 as default check
        await message.answer(get_msg("start.already_registered"), reply_markup=get_onboarding_choice_keyboard())
        return
        
    await message.answer(get_msg("start.welcome"), reply_markup=get_time_preset_keyboard())
    await state.set_state(OnboardingStates.waiting_for_time)

@router.callback_query(F.data == "setup:reset_confirm")
async def on_reset_confirm(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(get_msg("start.confirm_reset"), reply_markup=get_reset_confirm_keyboard())

@router.callback_query(F.data == "setup:reset_yes")
async def on_reset_yes(callback: CallbackQuery, habit_service: HabitService, state: FSMContext):
    await callback.answer()
    await habit_service.reset_user_data(callback.from_user.id)
    await callback.message.edit_text(get_msg("start.reset_success"))
    await callback.message.answer(get_msg("start.restart_onboarding"), reply_markup=get_time_preset_keyboard())
    await state.set_state(OnboardingStates.waiting_for_time)

@router.callback_query(OnboardingStates.waiting_for_time, F.data.startswith("time:"))
async def on_time_selected(callback: CallbackQuery, state: FSMContext, habit_service: HabitService):
    time_str = callback.data.split(":")[1] + ":" + callback.data.split(":")[2]
    await habit_service.update_user_time(callback.from_user.id, time_str)
    
    await callback.message.edit_text(get_msg("start.time_set", time=time_str), reply_markup=get_skip_keyboard())
    await state.set_state(OnboardingStates.adding_first_habit)

@router.callback_query(OnboardingStates.adding_first_habit, F.data == "setup:skip")
async def on_skip_habit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(get_msg("start.skip_habit"))
    await callback.message.answer(get_msg("start.setup_complete"), reply_markup=get_main_menu_keyboard())

@router.callback_query(F.data == "setup:time_manual")
async def on_time_manual(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(get_msg("start.time_manual_prompt"))
    await state.set_state(OnboardingStates.waiting_for_time)

@router.message(OnboardingStates.waiting_for_time)
async def on_time_input(message: Message, state: FSMContext, habit_service: HabitService):
    import re
    if not re.match(r"^\d{2}:\d{2}$", message.text):
        await message.answer(get_msg("start.time_invalid"))
        return
        
    await habit_service.update_user_time(message.from_user.id, message.text)
    await message.answer(get_msg("start.time_set", time=message.text), reply_markup=get_skip_keyboard())
    await state.set_state(OnboardingStates.adding_first_habit)

@router.message(F.text == "назад")
@router.message(F.text == "назад ↵")
@router.message(F.text == "/back")
async def on_back_text(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await message.answer(get_msg("statistics.menu_header"), reply_markup=get_main_menu_keyboard())
    # Clean menus AFTER sending the new keyboard to prevent jumping
    await _clean_menus(message, state, bot)

async def _clean_menus(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_ids = data.get("menu_msg_ids", [])
    for m in msg_ids:
        try:
            await bot.delete_message(message.chat.id, m)
        except Exception:
            pass
    try:
        await message.delete()
    except Exception:
        pass

@router.callback_query(F.data == "menu:main")
async def on_main_menu(callback_or_message, state: FSMContext, bot: Bot):
    await state.clear()
    text = get_msg("statistics.menu_header")
    kb = get_main_menu_keyboard()
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.answer()
        # Delete the trigger message for proper UX
        try:
            await callback_or_message.message.delete()
        except:
            pass
        await callback_or_message.message.answer(text, reply_markup=kb)
    else:
        await callback_or_message.answer(text, reply_markup=kb)
        await _clean_menus(callback_or_message, state, bot)
