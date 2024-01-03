from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


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
            data['session'] = session
            await handler(event, data)
            print('flag')
            await session.close()
        return
