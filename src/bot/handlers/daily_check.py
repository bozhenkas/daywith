import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.config.messages_loader import get_msg
from bot.keyboards.daily_kb import get_daily_check_keyboard
from bot.services.habit_service import HabitService
from bot.utils.date_utils import user_today

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("daily:done:"))
async def mark_habit_done(callback: CallbackQuery, habit_service: HabitService, user: dict) -> None:
    h_id = callback.data.split(":")[2]
    date_str = user_today(user.get("timezone", "Europe/Moscow"))
    await habit_service.mark_habit(callback.from_user.id, h_id, date_str, True)
    await callback.answer(get_msg("daily.habit_marked"))
    await _update_daily_message(callback, habit_service, date_str)


@router.callback_query(F.data.startswith("daily:skip:"))
async def mark_habit_skip(callback: CallbackQuery, habit_service: HabitService, user: dict) -> None:
    h_id = callback.data.split(":")[2]
    date_str = user_today(user.get("timezone", "Europe/Moscow"))
    await habit_service.mark_habit(callback.from_user.id, h_id, date_str, False)
    await callback.answer(get_msg("daily.habit_marked"))
    await _update_daily_message(callback, habit_service, date_str)


@router.callback_query(F.data.startswith("daily:info:"))
async def daily_habit_info(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data == "daily:noop")
async def daily_noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("daily:page:"))
async def daily_page(callback: CallbackQuery, habit_service: HabitService, user: dict) -> None:
    page = int(callback.data.split(":")[2])
    date_str = user_today(user.get("timezone", "Europe/Moscow"))
    habits = await habit_service.get_user_habits(callback.from_user.id)
    logs = await habit_service.get_daily_logs(callback.from_user.id, date_str)
    marked_ids = {str(log["habit_id"]) for log in logs}
    unmarked = [h for h in habits if str(h["_id"]) not in marked_ids]
    await callback.message.edit_reply_markup(reply_markup=get_daily_check_keyboard(unmarked, page))
    await callback.answer()


async def _update_daily_message(callback: CallbackQuery, habit_service: HabitService, date_str: str) -> None:
    habits = await habit_service.get_user_habits(callback.from_user.id)
    if not habits:
        return

    logs = await habit_service.get_daily_logs(callback.from_user.id, date_str)
    marked_ids = {str(log["habit_id"]) for log in logs}
    unmarked_habits = [h for h in habits if str(h["_id"]) not in marked_ids]

    if unmarked_habits:
        await callback.message.edit_reply_markup(reply_markup=get_daily_check_keyboard(unmarked_habits))
    else:
        await callback.message.edit_text(get_msg("daily.all_done", date=date_str), reply_markup=None)
