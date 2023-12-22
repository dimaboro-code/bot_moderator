from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Dict, Any, Callable, Awaitable
from core.config import Config


class AdminMiddleware(BaseMiddleware):
    def __init__(self, admins):
        print('mw', admins)
        self.admins = admins


    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data['admins'] = self.admins

        print('мв', data['admins'])

        return await handler(event, data)