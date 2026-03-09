from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime

from config.messages_loader import get_msg
from keyboards.daily_kb import get_daily_check_keyboard
from services.habit_service import HabitService

router = Router()

@router.callback_query(F.data.startswith("daily:done:"))
async def mark_habit_done(callback: CallbackQuery, habit_service: HabitService):
    h_id = callback.data.split(":")[2]
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    await habit_service.mark_habit(callback.from_user.id, h_id, date_str, True)
    await callback.answer(get_msg("daily.habit_marked"))
    await _update_daily_message(callback, habit_service, date_str)

@router.callback_query(F.data.startswith("daily:skip:"))
async def mark_habit_skip(callback: CallbackQuery, habit_service: HabitService):
    h_id = callback.data.split(":")[2]
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    await habit_service.mark_habit(callback.from_user.id, h_id, date_str, False)
    await callback.answer(get_msg("daily.habit_marked"))
    await _update_daily_message(callback, habit_service, date_str)

async def _update_daily_message(callback: CallbackQuery, habit_service: HabitService, date_str: str):
    habits = await habit_service.get_user_habits(callback.from_user.id)
    if not habits:
        return
        
    logs = await habit_service.get_daily_logs(callback.from_user.id, date_str)
    marked_ids = {str(log["habit_id"]): log["completed"] for log in logs}
    
    unmarked_habits = [h for h in habits if str(h["_id"]) not in marked_ids]
    
    if unmarked_habits:
        kb = get_daily_check_keyboard(unmarked_habits)
        await callback.message.edit_reply_markup(reply_markup=kb)
    else:
        text = get_msg("daily.digest_header", date=date_str) + "\nВсе отмечено!"
        await callback.message.edit_text(text, reply_markup=None)
