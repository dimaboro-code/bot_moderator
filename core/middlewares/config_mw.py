import json
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.enums import ChatAction
from aiogram.types import TelegramObject
from aiogram.exceptions import TelegramBadRequest
from ..redis import rclient

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
            try:
                if event.message is not None:
                    if event.message.from_user.username:
                        name = event.message.from_user.username
                    elif event.message.from_user.last_name:
                        name = event.message.from_user.first_name + ' ' + event.message.from_user.last_name
                    else:
                        name = event.message.from_user.first_name
                    text = event.message.text
                    tg_id = event.message.from_user.id
                    time = datetime.now()
                    data = rclient.get(tg_id)
                    if data is None:
                        data = {'text': text,
                                'tg_id': tg_id,
                                'name': name,
                                'time': time}
                        ex_time = time+timedelta(days=1)
                        rclient.set(tg_id, json.dumps(data), exat=ex_time.timestamp())
                        rclient.set(name, json.dumps(data), exat=ex_time.timestamp())
                else:
                    pass
            except Exception as e:
                print('no redis')
            data['session'] = session
            try:
                await handler(event, data)
            except TelegramBadRequest as e:
                with open('errors.log', 'a') as f:
                    f.write(f'Ошибка: {e} - запрос: {event.model_dump_json()}\n')
        return
