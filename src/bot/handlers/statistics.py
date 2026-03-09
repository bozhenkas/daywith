from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from bot.config.messages_loader import get_msg
from bot.services.statistics_service import StatisticsService
from bot.services.image_generator import StatsImageGenerator
from bot.services.habit_service import HabitService

router = Router()

@router.callback_query(F.data == "menu:stats")
async def show_statistics(callback: CallbackQuery, stats_service: StatisticsService, habit_service: HabitService):
    await callback.message.edit_text(get_msg("statistics.loading"))
    
    uid = callback.from_user.id
    user = await habit_service.repo.db.users.find_one({"telegram_id": uid})
    
    comp_rate = await stats_service.get_completion_rate(uid)
    best_habit = await stats_service.get_best_habit(uid)
    streaks = await stats_service.get_current_streaks(uid)
    cal_data = await stats_service.get_calendar_data(uid)
    
    stats_data = {
        "completion_rate": comp_rate,
        "best_habit": best_habit,
        "streaks": streaks,
        "calendar_data": cal_data
    }
    
    generator = StatsImageGenerator()
    img_bytes = generator.generate(user, stats_data)
    
    photo = BufferedInputFile(img_bytes, filename="stats.jpg")
    
    from bot.keyboards.main_menu import get_main_menu_keyboard
    await callback.message.delete()
    await callback.message.answer_photo(photo, caption="Твоя статистика!", reply_markup=get_main_menu_keyboard())
