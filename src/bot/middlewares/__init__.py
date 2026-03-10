import logging
from typing import Callable, Awaitable, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

logger = logging.getLogger(__name__)


class AddUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        habit_service = data.get("habit_service")
        update: Update = data.get("event_update")

        user = None
        if update and habit_service:
            tg_user = None
            if update.message:
                tg_user = update.message.from_user
            elif update.callback_query:
                tg_user = update.callback_query.from_user

            if tg_user:
                try:
                    user = await habit_service.get_or_create_user(
                        tg_id=tg_user.id,
                        username=tg_user.username,
                        first_name=tg_user.first_name,
                        last_name=tg_user.last_name,
                        lang_code=tg_user.language_code,
                        is_premium=tg_user.is_premium,
                    )
                except Exception as e:
                    logger.warning("AddUserMiddleware: failed to upsert user %s: %s", tg_user.id, e)

        data["user"] = user
        return await handler(event, data)
