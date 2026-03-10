from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from bot.config.messages_loader import get_msg
from bot.services.statistics_service import StatisticsService
from bot.services.image_generator import ImageGenerator
from bot.services.habit_service import HabitService
import os

router = Router()

@router.message(F.text == "статистика")
@router.callback_query(F.data == "menu:stats")
async def show_statistics(event: Message | CallbackQuery, stats_service: StatisticsService, habit_service: HabitService):
    if isinstance(event, CallbackQuery):
        await event.answer()
        msg = event.message
        uid = event.from_user.id
    else:
        msg = event
        uid = event.from_user.id

    loading_msg = await msg.answer(get_msg("statistics.loading"))
    
    # Ensure user exists in DB and has up-to-date username/name
    user = await habit_service.get_or_create_user(
        uid,
        event.from_user.username,
        event.from_user.first_name,
        last_name=event.from_user.last_name,
        lang_code=event.from_user.language_code,
        is_premium=event.from_user.is_premium
    )
    
    comp_rate = await stats_service.get_completion_rate(uid)
    best_habit = await stats_service.get_best_habit(uid)
    streaks = await stats_service.get_current_streaks(uid)
    cal_data = await stats_service.get_calendar_data(uid)
    
    stats_data = {
        "completion_rate": comp_rate,
        "best_habit": best_habit.get("name") if best_habit else "—",
        "streak": streaks.get(str(best_habit["_id"])) if best_habit else 0
    }
    
    assets_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
    generator = ImageGenerator(assets_path)
    img_path = await generator.generate_stats_image(uid, stats_data, cal_data)
    
    photo = FSInputFile(img_path)
    
    from bot.keyboards.main_menu import get_main_menu_keyboard
    await loading_msg.delete()
    await msg.answer_photo(photo, caption=get_msg("statistics.caption"), reply_markup=get_main_menu_keyboard())
    
    if os.path.exists(img_path):
        os.remove(img_path)
