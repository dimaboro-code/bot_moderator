# задачи
# Нужно отделять валидные сообщения от невалидных
# Валидные сообщения не обрабатываются
# Невалидные удаляются и помещаются в хранилище
# Пользователь имеет доступ к своему сообщению по клику на ссылку
# Ссылка ведет в личку, где диплинк достает сообщение из хранилища. Сообщение копируется по клику.
# При удалении бот говорит: сообщение не содержит тег и не является реплеем. Чтобы скопировать сообщение,
# перейдите по ссылке.
import json

from aiogram import Router, types, Bot

from core import ConfigVars
from core.filters.admin_filter import HashTagFilter, StrictChatFilter
from redis.asyncio import Redis

from core.utils.create_redis_pool import get_conn
from core.utils.delete_message_with_delay import delete_message

user_group_router = Router()


@user_group_router.message(StrictChatFilter(), HashTagFilter().__invert__())
async def strict_mode(message: types.Message, bot: Bot, reason_message: dict):
    async with get_conn() as redis:
        redis: Redis
        redis_message = await redis.get(message.from_user.id)
        if redis_message:
            list_msg: list = json.loads(redis_message)
        else:
            list_msg = []
        list_msg.append(message.model_dump_json())
        await redis.set(message.from_user.id, json.dumps(list_msg), ex=86400)
    try:
        await bot.delete_message(message.chat.id, reason_message.pop(message.chat.id))
    except Exception:
        pass
    msg = await message.answer('Сообщение не содержит теги #тема, #годнота или #вопрос, или не является '
                               'ответом на другое сообщение, поэтому оно было удалено. '
                               f'<a href="t.me/{str(ConfigVars.BOT_USERNAME)}?start=get_my_message">'
                               '\nОтправить удаленное сообщение в лс</a>', parse_mode='HTML',
                               disable_web_page_preview=True)
    reason_message[message.chat.id] = msg.message_id
    await message.delete()
    success = await delete_message(msg, 30)
    if success:
        reason_message.pop(message.chat.id)
