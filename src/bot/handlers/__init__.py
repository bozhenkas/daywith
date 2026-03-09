from aiogram import Router

from .start import router as start_router
from .habits import router as habits_router
from .daily_check import router as daily_router
from .history import router as history_router
from .settings import router as settings_router
from .statistics import router as statistics_router

def get_routers():
    return [
        start_router,
        habits_router,
        daily_router,
        history_router,
        settings_router,
        statistics_router
    ]
