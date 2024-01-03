from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from core.utils.id_recognizer import know_id
from core.utils.send_report import send_report_to_group


class AddUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        add = await know_id(event, session=data['session'])
        if not add:
            user_id = event.from_user.id
            username = event.from_user.username
            chat_id = event.chat.id
            chat_username = event.chat.username
            problem = 'Не удалось добавить пользователя в базу'
            await send_report_to_group(user_id, username, chat_id, chat_username, problem)

        return await handler(event, data)
