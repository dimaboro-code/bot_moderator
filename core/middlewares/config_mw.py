import asyncio
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, Update
from aiogram.exceptions import TelegramBadRequest

from core.config import engine
from core.database_functions.db_functions import add_id


class ConfigMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            if isinstance(event.message, Message):
                message = event.message
                if message.from_user.username:
                    username = message.from_user.username
                    tg_id = message.from_user.id
                    await add_id(username, tg_id)
        except Exception as e:
            print('no redis,', e)
        try:
            await handler(event, data)
        except TelegramBadRequest:
            await asyncio.sleep(8)
            await handler(event, data)
        finally:
            await engine.dispose()
        return
