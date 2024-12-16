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
from aiogram.enums import ChatType, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ChatJoinRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core import ConfigVars
from core.filters.filters import HashTagFilter, StrictChatFilter
from redis.asyncio import Redis

from core.models.data_models import Human
from core.services.ban import get_bh_keyboard
from core.utils.create_redis_pool import get_conn

user_group_router = Router()
user_group_router.message.filter(F.chat.type != ChatType.PRIVATE)


@user_group_router.chat_join_request()
async def captcha(request: ChatJoinRequest, bot: Bot):
    user_chat_id = request.user_chat_id
    print('request')
    hello_message = (
        "<b>Привет!</b>\n\n"
        "Я — бот-модератор сети чатов @slashdesigner. Через меня можно "
        "подтвердить заявку на вступление и снять блок.\n\n"
        "1. <b>Давай подтвердим твою заявку на вступление.</b> Если ты хочешь вступить в чаты, Нажми кнопку "
        "<code>/human</code>.\n\n"
        "Если ты не понимаешь, почему твои сообщения удаляются, прочитай закреп, например, "
        "<a href=\"https://t.me/figmachat/317401\">в Фигма-чате</a>.\n\n"
        "2. Если ты не можешь отправлять сообщения, ты в мьюте. Это режим, в котором ты можешь только читать чаты. "
        "Я помогу вернуть голос при помощи команды /unmute.\n\n"
        "3. Перед тем, как что-либо писать, тебе важно прочитать и понять наши правила, чтобы тебе не дали мьют.\n\n"
        "@figmachat — про Фигму как инструмент. "
        "<a href=\"https://slashdesigner.ru/figmachat\">Правила</a>.\n\n"
        "@designchat2 — про дизайн интерфейсов. "
        "<a href=\"https://slashdesigner.ru/designchat\">Правила</a>.\n\n"
        "@whatthefontt — опознаём шрифты по картинке. "
        "<a href=\"https://slashdesigner.ru/whatthefont\">Правила</a>.\n\n"
        "@slashimagineai — делимся промптами, обсуждаем возможности "
        "нейросетей. <a href=\"https://slashdesigner.ru/imagine\">Правила</a>."
    )
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Я человек',
        callback_data=Human(
            user_id=request.from_user.id,
            function='approve_request',
            chat_id=request.chat.id
        )
    )
    await bot.send_message(user_chat_id, hello_message, parse_mode=ParseMode.HTML, disable_web_page_preview=True,
                           reply_markup=builder.as_markup())


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
