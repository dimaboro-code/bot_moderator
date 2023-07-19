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

# версия с прода
# from aiogram import types
#
# from config import bot, CHATS, MUTE_SETTINGS
#
# from system_functions.delete_message import delete_message
# from system_functions.restrict import restrict
# from system_functions.is_username import is_username
#
# from db import *
#
#
# # init
# async def mute(moderator_message: types.Message):
#
#     # checking message formal conditions
#     # formal conditions - {replied message}: /mute {moderator message}
#     # Message isReply
#
#     # разбираем сообщение на составные части
#     # в сообщении может быть слово, начинающееся с символа @, а может не быть
#     # если слово есть, то мы мьютим пользователся по юзернейму
#     # если нет, то по реплею
#
#     username = is_username(moderator_message.text)
#
#     # if not moderator_message.reply_to_message:
#     #     tmp = await moderator_message.reply('Команда должна быть ответом на сообщение', )
#     #
#     #     await delete_message(tmp, 1)
#     #
#     #     # prevent function from muting a non-existing user
#     #     return
#
#     if username is not None:
#         user_id = get_id(username)
#     else:
#         user_id = moderator_message.reply_to_message.from_user.id
#     # Message hasMuteReason
#     if len(moderator_message.text.strip()) < 6:
#         # reason - any text after command, now could be just one letter
#         tmp = await moderator_message.answer('Нужно указать причину мьюта')
#         await delete_message(moderator_message, 1)
#         await delete_message(tmp, 1)
#
#         # prevent function from muting a user without a reason
#         return
#
#     # checking user status in current chat
#     # member object
#     member = await bot.get_chat_member(moderator_message.chat.id, user_id)
#
#     if member.status == 'restricted' and member.can_send_messages is False:
#         tmp = await moderator_message.answer('Пользователь уже в мьюте')
#
#         # delay 1 sec
#         await delete_message(tmp, 1)
#         return
#
#     # change permissions everywhere
#     for chat in CHATS:
#
#         try:
#             # check if user_id exsists in the chat
#             await bot.get_chat_member(chat, user_id)
#
#             # if a user isn't muted
#
#             # async mute action
#             await restrict(user_id, chat, MUTE_SETTINGS)
#
#         # if we catch bad request when user_id is not found we catch except and continue
#         except:
#
#             # we skip to next chat
#             continue
#
#     # in_database() - is Boolean
#     # if user doesn't exist (true)
#     if not await in_database(user_id):
#         # add him to database once
#         await add_user(user_id)
#
#     # dict to add to db
#     mute_data = {
#         'chat_id': moderator_message.chat.id,
#         'user_id': moderator_message.reply_to_message.from_user.id,
#         'message_id': moderator_message.reply_to_message.message_id,
#         'moderator_message': moderator_message.text[5:],
#         'admin_username': moderator_message.from_user.username
#     }
#
#     # add mute to database
#     await add_mute(mute_data)
#
#     success_message = await moderator_message.answer(
#         f'{moderator_message.reply_to_message.from_user.first_name} попал в мьют.'
#     )
#
#     # DELETE MESSAGES
#
#     try:
#         await bot.delete_message(
#             chat_id=moderator_message.chat.id,
#             message_id=moderator_message.reply_to_message.message_id
#         )
#     except:
#         # nu i pohui
#         pass
#
#     await delete_message(moderator_message)
#     await delete_message(success_message, 1)
#
