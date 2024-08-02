from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, Update
from aiogram.exceptions import TelegramBadRequest

from core.config import engine
from core.database_functions.db_functions import get_username, add_id


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
                elif message.from_user.last_name:
                    username = message.from_user.first_name + ' ' + message.from_user.last_name
                else:
                    username = message.from_user.first_name
                tg_id = message.from_user.id
                await add_id(username, tg_id)

        except Exception as e:
            print('no redis,', e)
        try:
            await handler(event, data)
            await engine.dispose()
        except TelegramBadRequest as e:
            print('бэд рекуест, ошибка ', e)
        return
