from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime

from config.messages_loader import get_msg
from keyboards.history_kb import get_date_navigation_keyboard
from services.habit_service import HabitService
from utils.date_utils import parse_date_str

router = Router()

@router.message(F.text == "история")
async def show_history_today(message: Message, habit_service: HabitService):
    today = datetime.utcnow()
    await _render_history(message, today, habit_service)

@router.callback_query(F.data.startswith("hist:prev:"))
@router.callback_query(F.data.startswith("hist:next:"))
async def navigate_history(callback: CallbackQuery, habit_service: HabitService):
    date_str = callback.data.split(":")[2]
    d = parse_date_str(date_str)
    await _render_history(callback, d, habit_service)

@router.callback_query(F.data == "hist:today")
async def navigate_today(callback: CallbackQuery, habit_service: HabitService):
    await _render_history(callback, datetime.utcnow(), habit_service)

async def _render_history(event, target_date: datetime, habit_service: HabitService):
    user_id = event.from_user.id
    date_str = target_date.strftime("%Y-%m-%d")
    logs = await habit_service.get_daily_logs(user_id, date_str)
    habits = await habit_service.get_user_habits(user_id, active_only=False)
    
    lines = [get_msg("history.header", date=date_str), ""]
    
    logs_map = {str(l["habit_id"]): l["completed"] for l in logs}
    
    for h in habits:
        h_id = str(h["_id"])
        if h_id in logs_map:
            status = "✓ выполнено" if logs_map[h_id] else "✗ пропущено"
            lines.append(f"{h['name']} - {status}")
        else:
            if not h["archived"] or h["created_at"].strftime("%Y-%m-%d") <= date_str:
                lines.append(f"{h['name']} - ⚪️ нет данных")
            
    text = "\n".join(lines)
    kb = get_date_navigation_keyboard(target_date)
    
    if hasattr(event, "message") and event.message:
        await event.message.edit_text(text, reply_markup=kb)
    else:
        await event.answer(text, reply_markup=kb)
