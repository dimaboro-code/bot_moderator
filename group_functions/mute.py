from aiogram import types

from config import bot, CHATS, MUTE_SETTINGS

from system_functions.delete_message import delete_message
from system_functions.restrict import restrict
from system_functions.is_username import is_username

from db import *


# init
async def mute(moderator_message: types.Message):

    # checking message formal conditions
    # formal conditions - {replied message}: /mute {moderator message}
    # Message isReply

    # разбираем сообщение на составные части
    # в сообщении может быть слово, начинающееся с символа @, а может не быть
    # если слово есть, то мы мьютим пользователся по юзернейму
    # если нет, то по реплею

    username = is_username(moderator_message.text)

    if not moderator_message.reply_to_message:
        tmp = await moderator_message.reply('Команда должна быть ответом на сообщение', )

        await delete_message(tmp, 1)

        # prevent function from muting a non-existing user
        return

    if username is not None:
        user_id = bot.get_chat_member(username)
    else:
        user_id = moderator_message.reply_to_message.from_user.id
    # Message hasMuteReason
    if len(moderator_message.text.strip()) < 6:
        # reason - any text after command, now could be just one letter
        tmp = await moderator_message.answer('Нужно указать причину мьюта')
        await delete_message(moderator_message, 1)
        await delete_message(tmp, 1)

        # prevent function from muting a user without a reason
        return

    # checking user status in current chat
    # member ojbect
    member = await bot.get_chat_member(moderator_message.chat.id, user_id)

    if member.status == 'restricted' and member.can_send_messages is False:
        tmp = await moderator_message.answer('Пользователь уже в мьюте')

        # delay 1 sec
        await delete_message(tmp, 1)
        return

    # change permissions everywhere
    for chat in CHATS:

        try:
            # check if user_id exsists in the chat
            await bot.get_chat_member(chat, user_id)

            # if a user isn't muted

            # async mute action
            await restrict(user_id, chat, MUTE_SETTINGS)


        # if we catch bad request when user_id is not found we catch except and continue
        except:

            # we skip to next chat
            continue

    # in_database() - is Boolean
    # if user doesn't exist (true)
    if not await in_database(user_id):
        # add him to database once
        await add_user(user_id)

    # dict to add to db
    mute_data = {
        'chat_id': moderator_message.chat.id,
        'user_id': moderator_message.reply_to_message.from_user.id,
        'message_id': moderator_message.reply_to_message.message_id,
        'moderator_message': moderator_message.text[5:],
        'admin_username': moderator_message.from_user.username
    }

    # add mute to database
    await add_mute(mute_data)

    success_message = await moderator_message.answer(
        f'{moderator_message.reply_to_message.from_user.first_name} попал в мьют.'
    )

    # DELETE MESSAGES

    try:
        await bot.delete_message(
            chat_id=moderator_message.chat.id,
            message_id=moderator_message.reply_to_message.message_id
        )
    except:
        # nu i pohui
        pass

    await delete_message(moderator_message)

    await delete_message(success_message, 1)
