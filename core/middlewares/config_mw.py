from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, Update
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from core.database_functions.db_functions import get_username, add_id


# отсюда нужно создавать сессию бд, которую потом пробрасывать дальше
class ConfigMiddleware(BaseMiddleware):
    def __init__(self, async_session: async_sessionmaker[AsyncSession]):
        self.session = async_session

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        async with self.session() as session:
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
                    user = await get_username(tg_id, session)
                    if not user:
                        await add_id(username, tg_id, session)

            except Exception as e:
                print('no redis,', e)
            data['session'] = session
            try:
                await handler(event, data)
            except TelegramBadRequest as e:
                print('бэд рекуест, ошибка ', e)
        return
