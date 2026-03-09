from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from bot.config.messages_loader import get_msg
from datetime import datetime

class DigestScheduler:
    def __init__(self, bot: Bot, habit_service):
        self.scheduler = AsyncIOScheduler()
        self.bot = bot
        self.habit_service = habit_service

    def start(self):
        self.scheduler.add_job(
            self.send_digests,
            'cron',
            minute='*',
            id='minute_checker'
        )
        self.scheduler.start()

    async def send_digests(self):
        now_str = datetime.utcnow().strftime("%H:%M")
        users = await self.habit_service.get_all_users_for_digest(now_str)
        
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        
        from bot.keyboards.daily_kb import get_daily_check_keyboard
        
        for u in users:
            habits = await self.habit_service.get_user_habits(u["telegram_id"])
            if not habits:
                continue
            
            kb = get_daily_check_keyboard(habits)
            text = get_msg("daily.digest_header", date=date_str)
            try:
                await self.bot.send_message(
                    chat_id=u["telegram_id"],
                    text=text,
                    reply_markup=kb
                )
            except Exception as e:
                print(f"Failed to send digest to {u['telegram_id']}: {e}")
