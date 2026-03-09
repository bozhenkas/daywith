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
from aiogram import Bot

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, habit_service: HabitService):
    user = await habit_service.get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name
    )
    
    if "is_new" in user:  # Simplification for logic check
        pass
        
    await message.answer(get_msg("start.welcome"), reply_markup=get_time_preset_keyboard())
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

@router.message(F.text == "назад")
@router.message(F.text == "назад ↵")
async def on_back_text(message: Message, state: FSMContext, bot: Bot):
    await _clean_menus(message, state, bot)
    await state.clear()
    await message.answer("главное меню:", reply_markup=get_main_menu_keyboard())

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

@router.message(F.text == "главное меню:")
@router.callback_query(F.data == "menu:main")
async def on_main_menu(callback_or_message, state: FSMContext, bot: Bot):
    await state.clear()
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.answer()
        await callback_or_message.message.answer("главное меню:", reply_markup=get_main_menu_keyboard())
    else:
        # If it's a message, process cleanups just in case
        await _clean_menus(callback_or_message, state, bot)
        await callback_or_message.answer("главное меню:", reply_markup=get_main_menu_keyboard())
