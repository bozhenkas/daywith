from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.config.messages_loader import get_msg
from bot.keyboards.habits_kb import get_habits_list_keyboard, get_habit_type_keyboard, get_habit_edit_keyboard
from bot.keyboards.main_menu import get_main_menu_keyboard, get_back_reply_keyboard
from bot.fsm.states import HabitStates, OnboardingStates
from bot.services.habit_service import HabitService

router = Router()

@router.message(F.text == "мои привычки")
async def show_habits(message: Message, habit_service: HabitService, state: FSMContext):
    msg1 = await message.answer("ℹ", reply_markup=get_back_reply_keyboard())
    habits = await habit_service.get_user_habits(message.from_user.id)
    text = get_msg("habits.list_header") if habits else get_msg("habits.list_empty")
    msg2 = await message.answer(text, reply_markup=get_habits_list_keyboard(habits))
    await state.update_data(menu_msg_ids=[msg1.message_id, msg2.message_id])

@router.callback_query(F.data == "habit:add")
async def start_add_habit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
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
    await callback.answer()
    h_type = callback.data.split(":")[1]
    data = await state.get_data()
    name = data.get("habit_name", "без названия")
    
    await habit_service.create_habit(callback.from_user.id, name, h_type, 7)
    
    # Stay in the loop
    await state.set_state(HabitStates.waiting_for_name)
    await callback.message.edit_text(get_msg("habits.add_success", habit_name=name))

@router.callback_query(F.data.startswith("habit:edit:"))
async def edit_habit(callback: CallbackQuery, habit_service: HabitService):
    await callback.answer()
    h_id = callback.data.split(":")[2]
    h = await habit_service.get_habit(h_id)
    if not h:
        await callback.answer(get_msg("errors.not_found"), show_alert=True)
        return
        
    text = get_msg("habits.habit_info", icon="", name=h["name"], goal=h["goal_count"]).strip()
    await callback.message.edit_text(text, reply_markup=get_habit_edit_keyboard(h_id))

@router.callback_query(F.data.startswith("habit:del:"))
async def delete_habit(callback: CallbackQuery, habit_service: HabitService):
    h_id = callback.data.split(":")[2]
    h = await habit_service.get_habit(h_id)
    if h:
        await habit_service.archive_habit(h_id)
        await callback.answer(get_msg("habits.archived", habit_name=h["name"]))
    else:
        await callback.answer()
    
    habits = await habit_service.get_user_habits(callback.from_user.id)
    text = get_msg("habits.list_header") if habits else get_msg("habits.list_empty")
    await callback.message.edit_text(text, reply_markup=get_habits_list_keyboard(habits))

@router.callback_query(F.data == "habit:cancel_add")
async def cancel_add(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("отменено.")
