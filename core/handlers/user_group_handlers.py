# задачи
# Нужно отделять валидные сообщения от невалидных
# Валидные сообщения не обрабатываются
# Невалидные удаляются и помещаются в хранилище
# Пользователь имеет доступ к своему сообщению по клику на ссылку
# Ссылка ведет в личку, где диплинк достает сообщение из хранилища. Сообщение копируется по клику.
# При удалении бот говорит: сообщение не содержит тег и не является реплеем. Чтобы скопировать сообщение,
# перейдите по ссылке.
# При входе в чат бот тоже говорит - чтобы не лишиться права писать сообщения, прочти правила
import json

from aiogram import Router, types, Bot

from core import ConfigVars
from core.filters.admin_filter import HashTagFilter, StrictChatFilter
from redis.asyncio import Redis

from core.utils.create_redis_pool import get_conn
from core.utils.delete_message_with_delay import delete_message

user_group_router = Router()


@user_group_router.message(StrictChatFilter(), HashTagFilter().__invert__())
async def echo_group(message: types.Message, bot: Bot):
    msg = await message.reply(f'Невалидное сообщение. Чтобы восстановить, нажмите '
                              f'<a href="t.me/{str(ConfigVars.BOT_USERNAME)}?start=get_my_message">'
                              f'сюда</a>', parse_mode='HTML')
    async with get_conn() as redis:
        redis: Redis
        redis_message = await redis.get(message.from_user.id)
        if redis_message:
            list_msg: list = json.loads(redis_message)
        else:
            list_msg = []
        list_msg.append(message.model_dump_json())
        await redis.set(message.from_user.id, json.dumps(list_msg), ex=86400)
    await message.delete()
    await delete_message(msg, 5)


@user_group_router.message()
async def echo_group(message: types.Message, bot: Bot):
    await message.reply('Все ок')