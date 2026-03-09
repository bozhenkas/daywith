from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config.messages_loader import get_msg
from keyboards.habits_kb import get_habits_list_keyboard, get_habit_type_keyboard, get_habit_edit_keyboard
from keyboards.main_menu import get_main_menu_keyboard
from fsm.states import HabitStates, OnboardingStates
from services.habit_service import HabitService

router = Router()

@router.message(F.text == "мои привычки")
async def show_habits(message: Message, habit_service: HabitService):
    habits = await habit_service.get_user_habits(message.from_user.id)
    text = get_msg("habits.list_header") if habits else get_msg("habits.list_empty")
    await message.answer(text, reply_markup=get_habits_list_keyboard(habits))

@router.callback_query(F.data == "habit:add")
async def start_add_habit(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(get_msg("habits.add_prompt"))
    await state.set_state(HabitStates.waiting_for_name)

@router.message(HabitStates.waiting_for_name)
@router.message(OnboardingStates.adding_first_habit)
async def process_habit_name(message: Message, state: FSMContext):
    if not message.text:
        return
    await state.update_data(habit_name=message.text)
    await message.answer(get_msg("habits.choose_type"), reply_markup=get_habit_type_keyboard())
    await state.set_state(HabitStates.choosing_type)

@router.callback_query(HabitStates.choosing_type, F.data.startswith("htype:"))
async def process_habit_type(callback: CallbackQuery, state: FSMContext, habit_service: HabitService):
    h_type = callback.data.split(":")[1]
    data = await state.get_data()
    name = data.get("habit_name", "без названия")
    
    await habit_service.create_habit(callback.from_user.id, name, h_type, 7)
    
    # Stay in the loop
    await state.set_state(HabitStates.waiting_for_name)
    await callback.message.edit_text(get_msg("habits.add_success", habit_name=name))

@router.callback_query(F.data.startswith("habit:edit:"))
async def edit_habit(callback: CallbackQuery, habit_service: HabitService):
    h_id = callback.data.split(":")[2]
    h = await habit_service.get_habit(h_id)
    if not h:
        await callback.answer(get_msg("errors.not_found"), show_alert=True)
        return
        
    icon = "✅" if h["type"] == "good" else "❌"
    text = get_msg("habits.habit_info", icon=icon, name=h["name"], goal=h["goal_count"])
    await callback.message.edit_text(text, reply_markup=get_habit_edit_keyboard(h_id))

@router.callback_query(F.data.startswith("habit:del:"))
async def delete_habit(callback: CallbackQuery, habit_service: HabitService):
    h_id = callback.data.split(":")[2]
    h = await habit_service.get_habit(h_id)
    if h:
        await habit_service.archive_habit(h_id)
        await callback.answer(get_msg("habits.archived", habit_name=h["name"]))
    
    habits = await habit_service.get_user_habits(callback.from_user.id)
    text = get_msg("habits.list_header") if habits else get_msg("habits.list_empty")
    await callback.message.edit_text(text, reply_markup=get_habits_list_keyboard(habits))

@router.callback_query(F.data == "habit:cancel_add")
async def cancel_add(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("отменено.")
