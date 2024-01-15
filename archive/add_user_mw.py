from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from core.utils.add_user_to_db import add_user_to_db
from core.utils.send_report import send_bug_report


class AddUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        add = await add_user_to_db(event, session=data['session'])
        if not add:
            user_id = event.from_user.id
            username = event.from_user.username
            chat_id = event.chat.id
            chat_username = event.chat.username
            problem = 'Не удалось добавить пользователя в базу'
            await send_bug_report(user_id, username, chat_id, chat_username, problem)

        return await handler(event, data)
