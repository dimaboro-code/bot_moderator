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

user_group_router = Router()


@user_group_router.message(StrictChatFilter(), HashTagFilter().__invert__())
async def strict_mode(message: types.Message, bot: Bot):

    message_copy = await bot.forward_message(
        ConfigVars.MESSAGE_CONTAINER_CHAT, from_chat_id=message.chat.id, message_id=message.message_id
    )
    async with get_conn() as redis:
        redis: Redis
        redis_message = await redis.get(message.from_user.id)
        if redis_message:
            list_msg: list = json.loads(redis_message)
        else:
            list_msg = []
        list_msg.append(message_copy.message_id)
        await redis.set(message.from_user.id, json.dumps(list_msg), ex=86400)
    # msg = await message.answer(
    #     'Привет, @username! В чате действует функция Strict Reply, смотри правила (slashdesigner.ru/designchat).'
    #     ' Пришлось удалить твоё сообщение, потому что оно не было ответом на другое, либо не содержало хэштегов, '
    #     'которыми мы начинаем новые треды: #тема, #годнота #вопрос или #ревью. Я сохранил его и могу переслать его тебе'
    #     ' в течение суток. \n'
    #     f'<a href="t.me/{str(ConfigVars.BOT_USERNAME)}?start=get_my_message">'
    #     '\nВосстановить</a>', parse_mode='HTML',
    #     disable_web_page_preview=True
    # )
    await message.delete()
