from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.config.messages_loader import get_msg
from bot.keyboards.habits_kb import (
    get_habits_list_keyboard,
    get_habit_type_keyboard,
    get_habit_edit_keyboard,
    get_habit_goal_keyboard,
    get_cancel_add_keyboard,
)
from bot.keyboards.main_menu import get_main_menu_keyboard, get_back_reply_keyboard
from bot.fsm.states import HabitStates, OnboardingStates
from bot.services.habit_service import HabitService

router = Router()


def _habits_text(habits: list) -> str:
    return get_msg("habits.list_header" if habits else "habits.list_empty")


@router.message(F.text == "мои привычки")
async def show_habits(message: Message, habit_service: HabitService, state: FSMContext) -> None:
    msg1 = await message.answer(get_msg("habits.info_emoji"), reply_markup=get_back_reply_keyboard(), disable_notification=True)
    habits = await habit_service.get_user_habits(message.from_user.id)
    msg2 = await message.answer(_habits_text(habits), reply_markup=get_habits_list_keyboard(habits))
    await state.update_data(menu_msg_ids=[msg1.message_id, msg2.message_id])


@router.callback_query(F.data == "menu:habits")
async def show_habits_callback(callback: CallbackQuery, habit_service: HabitService) -> None:
    await callback.answer()
    habits = await habit_service.get_user_habits(callback.from_user.id)
    await callback.message.edit_text(_habits_text(habits), reply_markup=get_habits_list_keyboard(habits))


@router.callback_query(F.data == "habit:add")
async def start_add_habit(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.answer(get_msg("habits.add_prompt"), reply_markup=get_cancel_add_keyboard())
    await state.set_state(HabitStates.waiting_for_name)


@router.message(HabitStates.waiting_for_name)
@router.message(OnboardingStates.adding_first_habit)
async def process_habit_name(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(habit_name=message.text)
    await message.answer(get_msg("habits.choose_type"), reply_markup=get_habit_type_keyboard())
    await state.set_state(HabitStates.choosing_type)


@router.callback_query(HabitStates.choosing_type, F.data.startswith("htype:"))
async def process_habit_type(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    h_type = callback.data.split(":")[1]
    await state.update_data(habit_type=h_type)
    await callback.message.edit_text(get_msg("habits.choose_goal"), reply_markup=get_habit_goal_keyboard())
    await state.set_state(HabitStates.setting_goal)


@router.callback_query(HabitStates.setting_goal, F.data.startswith("hgoal:"))
async def process_habit_goal(callback: CallbackQuery, state: FSMContext, habit_service: HabitService) -> None:
    await callback.answer()
    goal = int(callback.data.split(":")[1])
    data = await state.get_data()
    name = data.get("habit_name", get_msg("habits.unknown_name"))
    h_type = data.get("habit_type", "good")
    await habit_service.create_habit(callback.from_user.id, name, h_type, goal)
    await state.set_state(HabitStates.waiting_for_name)
    await callback.message.edit_text(get_msg("habits.add_success", habit_name=name), reply_markup=get_cancel_add_keyboard())


@router.callback_query(F.data.startswith("habit:edit:"))
async def edit_habit(callback: CallbackQuery, habit_service: HabitService) -> None:
    await callback.answer()
    h_id = callback.data.split(":")[2]
    h = await habit_service.get_habit(h_id)
    if not h:
        await callback.answer(get_msg("errors.not_found"), show_alert=True)
        return
    text = get_msg("habits.habit_info", icon="", name=h["name"]).strip()
    await callback.message.edit_text(text, reply_markup=get_habit_edit_keyboard(h_id))


@router.callback_query(F.data.startswith("habit:rename:"))
async def start_rename_habit(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    h_id = callback.data.split(":")[2]
    await state.update_data(rename_habit_id=h_id)
    await callback.message.edit_text(get_msg("habits.rename_prompt"))
    await state.set_state(HabitStates.waiting_for_rename)


@router.message(HabitStates.waiting_for_rename)
async def process_rename_habit(message: Message, state: FSMContext, habit_service: HabitService) -> None:
    if not message.text:
        return
    data = await state.get_data()
    h_id = data.get("rename_habit_id")
    await habit_service.rename_habit(h_id, message.text)
    await state.clear()
    habits = await habit_service.get_user_habits(message.from_user.id)
    await message.answer(get_msg("habits.rename_success", habit_name=message.text))
    await message.answer(_habits_text(habits), reply_markup=get_habits_list_keyboard(habits))


@router.callback_query(F.data.startswith("habit:del:"))
async def delete_habit(callback: CallbackQuery, habit_service: HabitService) -> None:
    h_id = callback.data.split(":")[2]
    h = await habit_service.get_habit(h_id)
    if h:
        await habit_service.archive_habit(h_id)
        await callback.answer(get_msg("habits.archived", habit_name=h["name"]))
    else:
        await callback.answer()
    habits = await habit_service.get_user_habits(callback.from_user.id)
    await callback.message.edit_text(_habits_text(habits), reply_markup=get_habits_list_keyboard(habits))


@router.callback_query(F.data.startswith("habit:page:"))
async def habits_page(callback: CallbackQuery, habit_service: HabitService) -> None:
    await callback.answer()
    page = int(callback.data.split(":")[2])
    habits = await habit_service.get_user_habits(callback.from_user.id)
    await callback.message.edit_text(_habits_text(habits), reply_markup=get_habits_list_keyboard(habits, page))


@router.callback_query(F.data == "habit:noop")
async def noop_habit(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data == "habit:cancel_add")
async def cancel_add(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(get_msg("habits.canceled"))
