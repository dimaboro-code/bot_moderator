from aiogram import types

from config import bot, CHATS, MUTE_SETTINGS

from system_functions.delete_message import delete_message
from system_functions.restrict import restrict
from system_functions.is_username import is_username

from db import *


async def mute(moderator_message: types.Message):
    """
    Функция для выполнения команды /mute и мьюта пользователя.

    Args:
        moderator_message: Объект types.Message с сообщением модератора.

    """
    username = is_username(moderator_message.text)
    print(username)

    if username is not None:
        user_id = await get_id(username)
        print(user_id)
    else:
        if not moderator_message.reply_to_message:
            tmp = await moderator_message.reply('Команда должна быть ответом на сообщение')
            await delete_message(tmp, 1)
            return

        user_id = moderator_message.reply_to_message.from_user.id


    if len(moderator_message.text.strip().split()) < 2:
        ans = await moderator_message.answer('Нужно указать причину мьюта')
        await delete_message(ans, 1)
        await delete_message(moderator_message, 1)
        return

    member = await bot.get_chat_member(moderator_message.chat.id, user_id)

    if member.status == 'restricted' and not member.can_send_messages:
        async with moderator_message.answer('Пользователь уже в мьюте') as ans:
            await delete_message(ans, 1)
        return

    for chat in CHATS:
        try:
            await bot.get_chat_member(chat, user_id)
            await restrict(user_id, chat, MUTE_SETTINGS)
        except:
            continue

    if not await in_database(user_id):
        await add_user(user_id)

    mute_data = {
        'chat_id': moderator_message.chat.id,
        'user_id': user_id,
        'message_id': 00000,
        'moderator_message': moderator_message.text[5:],
        'admin_username': moderator_message.from_user.username
    }

    await add_mute(mute_data)

    if username is None:
        name_of_user = moderator_message.reply_to_message.from_user.first_name
    else:
        name_of_user = username

    success_message = await moderator_message.answer(
        f'{name_of_user} попал в мьют.'
    )

    try:
        await bot.delete_message(
            chat_id=moderator_message.chat.id,
            message_id=moderator_message.reply_to_message.message_id
        )
        await delete_message(moderator_message)
        await delete_message(success_message, 1)
    except:
        pass
