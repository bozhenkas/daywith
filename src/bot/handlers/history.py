from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from datetime import datetime

from bot.config.messages_loader import get_msg
from bot.keyboards.history_kb import get_date_navigation_keyboard
from bot.keyboards.main_menu import get_back_reply_keyboard
from bot.services.habit_service import HabitService
from bot.utils.date_utils import parse_date_str
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(F.text == "история")
async def show_history_today(message: Message, habit_service: HabitService, state: FSMContext):
    msg1 = await message.answer(get_msg("habits.info_emoji"), reply_markup=get_back_reply_keyboard(), disable_notification=True)
    today = datetime.utcnow()
    await _render_history(message, today, habit_service, state=state, msg1=msg1)

@router.callback_query(F.data.startswith("hist:prev:"))
@router.callback_query(F.data.startswith("hist:next:"))
async def navigate_history(callback: CallbackQuery, habit_service: HabitService):
    await callback.answer()
    date_str = callback.data.split(":")[2]
    d = parse_date_str(date_str)
    await _render_history(callback, d, habit_service)

@router.callback_query(F.data == "hist:today")
async def navigate_today(callback: CallbackQuery, habit_service: HabitService):
    await callback.answer()
    await _render_history(callback, datetime.utcnow(), habit_service)

@router.callback_query(F.data == "hist:noop")
@router.callback_query(F.data == "hist:pick")
async def noop_history(callback: CallbackQuery):
    await callback.answer()

async def _render_history(event, target_date: datetime, habit_service: HabitService, state: FSMContext = None, msg1: Message = None):
    user_id = event.from_user.id
    date_str = target_date.strftime("%Y-%m-%d")
    logs = await habit_service.get_daily_logs(user_id, date_str)
    habits = await habit_service.get_user_habits(user_id, active_only=True)
    
    lines = [get_msg("history.header", date=date_str), ""]
    
    logs_map = {str(l["habit_id"]): l["completed"] for l in logs}
    
    for h in habits:
        h_id = str(h["_id"])
        if h_id in logs_map:
            status = get_msg("history.done") if logs_map[h_id] else get_msg("history.skipped")
            lines.append(f"{h['name']} - {status}")
        else:
            if not h["archived"] or h["created_at"].strftime("%Y-%m-%d") <= date_str:
                lines.append(f"{h['name']} - {get_msg('history.no_data')}")
            
    text = "\n".join(lines)
    kb = get_date_navigation_keyboard(target_date)
    
    if hasattr(event, "message") and event.message:
        msg2 = await event.message.edit_text(text, reply_markup=kb)
        if state and msg1:
            await state.update_data(menu_msg_ids=[msg1.message_id, msg2.message_id])
    else:
        msg2 = await event.answer(text, reply_markup=kb)
        if state and msg1:
            await state.update_data(menu_msg_ids=[msg1.message_id, msg2.message_id])
