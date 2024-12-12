# задачи
# Нужно отделять валидные сообщения от невалидных
# Валидные сообщения не обрабатываются
# Невалидные удаляются и помещаются в хранилище
# Пользователь имеет доступ к своему сообщению по клику на ссылку
# Ссылка ведет в личку, где диплинк достает сообщение из хранилища. Сообщение копируется по клику.
# При удалении бот говорит: сообщение не содержит тег и не является реплеем. Чтобы скопировать сообщение,
# перейдите по ссылке.


import json

from aiogram import Router, types, Bot, F
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ChatJoinRequest

from core import ConfigVars
from core.filters.filters import HashTagFilter, StrictChatFilter
from redis.asyncio import Redis

from core.services.ban import get_bh_keyboard
from core.utils.create_redis_pool import get_conn

user_group_router = Router()
user_group_router.message.filter(F.chat.type != ChatType.PRIVATE)


@user_group_router.chat_join_request()
async def captcha(request: ChatJoinRequest, bot: Bot):
    chat_name = request.chat.title
    user_chat_id = request.user_chat_id
    print('request')
    message = (f'Здравствуйте!\n\nВы подали заявку на вступление в чат {chat_name}.\n'
               'Для того, чтобы вступить в чат, прочтите правила сообщества, '
               'затем отправьте мне команду /imnotaspammer.'
               'правила сообщества доступны в закрепленном сообщении в чате или по команде /start')
    await bot.send_message(user_chat_id, message)



@user_group_router.message(StrictChatFilter(), HashTagFilter().__invert__())
async def strict_mode(message: types.Message, bot: Bot, admins: list[int]):
    user_id = message.from_user.id
    builder = get_bh_keyboard(user_id)
    try:
        if message.from_user.id in admins:
            keyboard = None
        else:
            keyboard = builder.as_markup()
        message_copy: types.MessageId = await bot.copy_message(
            ConfigVars.MESSAGE_CONTAINER_CHAT, from_chat_id=message.chat.id, message_id=message.message_id,
            reply_markup=keyboard
        )
    except TelegramBadRequest:
        return
    async with get_conn() as redis:
        redis: Redis
        redis_message = await redis.get(message.from_user.id)
        if redis_message:
            list_msg: list = json.loads(redis_message)
        else:
            list_msg = []
        list_msg.append(message_copy.message_id)
        await redis.set(message.from_user.id, json.dumps(list_msg), ex=86400)
    await message.delete()

# # оставить в комментах пока
# @user_group_router.message()
# async def strict_mode(message: types.Message, bot: Bot):
#     msg = str(message.model_dump())
#     string = [msg[i:i + 4096] for i in range(0, len(msg), 4096)]
#     for msg in string:
#         await message.answer(msg)
