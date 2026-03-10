import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from bot.config.messages_loader import get_msg
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


class DigestScheduler:
    def __init__(self, bot: Bot, habit_service):
        self.scheduler = AsyncIOScheduler()
        self.bot = bot
        self.habit_service = habit_service

    def start(self):
        self.scheduler.add_job(
            self.send_digests,
            "cron",
            minute="*",
            id="minute_checker",
        )
        self.scheduler.start()

    async def send_digests(self):
        users = await self.habit_service.get_all_notif_users()

        from bot.keyboards.daily_kb import get_daily_check_keyboard

        for u in users:
            tz_str = u.get("timezone", "Europe/Moscow")
            try:
                tz = ZoneInfo(tz_str)
            except Exception:
                tz = ZoneInfo("Europe/Moscow")

            user_now = datetime.now(tz)
            user_time_str = user_now.strftime("%H:%M")
            user_date_str = user_now.strftime("%Y-%m-%d")

            if u.get("digest_time") != user_time_str:
                continue

            habits = await self.habit_service.get_user_habits(u["telegram_id"])
            if not habits:
                continue

            kb = get_daily_check_keyboard(habits)
            text = get_msg("daily.digest_header", date=user_date_str)
            try:
                await self.bot.send_message(
                    chat_id=u["telegram_id"],
                    text=text,
                    reply_markup=kb,
                )
            except Exception as e:
                logger.warning("Failed to send digest to %s: %s", u["telegram_id"], e)
