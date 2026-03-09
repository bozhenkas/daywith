import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config.settings import load_settings
from bot.config.messages_loader import MessageManager
from database.mongo import MongoRepo
from bot.services.habit_service import HabitService
from bot.services.statistics_service import StatisticsService
from bot.services.scheduler import DigestScheduler
from bot.handlers import get_routers

async def inject_services(handler, event, data):
    data['habit_service'] = data.get('habit_service')
    data['stats_service'] = data.get('stats_service')
    return await handler(event, data)

async def main():
    settings = load_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level))
    
    MessageManager.load()
    
    db_repo = MongoRepo(settings.mongo_uri, settings.mongo_db_name)
    await db_repo.init_indexes()
    
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    
    habit_service = HabitService(db_repo)
    stats_service = StatisticsService(db_repo)
    
    dp.update.outer_middleware(inject_services)
    
    workflow_data = {
        "habit_service": habit_service,
        "stats_service": stats_service
    }
    
    for router in get_routers():
        dp.include_router(router)
        
    scheduler = DigestScheduler(bot, habit_service)
    scheduler.start()
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, **workflow_data)
    finally:
        db_repo.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
