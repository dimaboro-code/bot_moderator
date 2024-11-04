import asyncio
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, Update
from aiogram.exceptions import TelegramBadRequest

from core.utils.add_user_to_db import add_user_to_db
from core.database_functions.db_models import engine


class ConfigMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event.message, Message):
            message = event.message
            if message.from_user.username:
                await add_user_to_db(message=message, bot=data['bot'])
        try:
            await handler(event, data)
        except TelegramBadRequest:
            await asyncio.sleep(8)
            await handler(event, data)
        finally:
            await engine.dispose()
