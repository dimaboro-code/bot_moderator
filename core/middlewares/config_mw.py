from datetime import datetime
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, Update
from aiogram.exceptions import TelegramBadRequest
from redis_om import Migrator

from core.database_functions.redis1 import RedisUser


# отсюда нужно создавать сессию бд, которую потом пробрасывать дальше
class ConfigMiddleware(BaseMiddleware):
    def __init__(self, async_session):
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
                        name = message.from_user.username
                    elif message.from_user.last_name:
                        name = message.from_user.first_name + ' ' + message.from_user.last_name
                    else:
                        name = message.from_user.first_name
                    tg_id = message.from_user.id
                    time_msg = datetime.now()
                    print(name, tg_id, time_msg)
                    Migrator().run()
                    user_list = RedisUser.find(RedisUser.tg_id == tg_id).all()
                    if len(user_list) == 0:
                        user = RedisUser(username=name, tg_id=tg_id, time_msg=time_msg)
                    else:
                        user = user_list[0]
                        user.time_msg = time_msg
                    user.update()
                    user.expire(36000)
            except Exception as e:
                print('no redis,', e)
            data['session'] = session
            try:
                await handler(event, data)
            except TelegramBadRequest as e:
                print('бэд рекуест, ошибка ', e)
            # except Exception as e:
            #     print(f'Не работает, ошибка: {e}')
        return
