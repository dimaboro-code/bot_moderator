from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.exceptions import TelegramBadRequest

from core.utils.add_user_to_db import add_user_to_db


# отсюда нужно создавать сессию бд, которую потом пробрасывать дальше
class ConfigMiddleware(BaseMiddleware):
    def __init__(self, async_session):
        self.session = async_session

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with self.session() as session:
            if event.message:
                await add_user_to_db(event.message, session)
            data['session'] = session
            for _ in range(3):
                try:
                    await handler(event, data)
                    break
                except TelegramBadRequest as e:
                    print('бэд рекуест, ошибка ', e)
                    continue
                except Exception as e:
                    print(f'Не работает, ошибка: {e}')
        return
