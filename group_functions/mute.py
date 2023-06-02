
import aiogram

from aiogram import types

from config import bot, CHATS, MUTE_SETTINGS

from system_functions.delete_message import delete_message
from system_functions.restrict import restrict

from db import *

# init
async def mute(message: types.Message):
    
    user_id = message.reply_to_message.from_user.id
    
    # checking message formal conditions 
    # Message isReply
    if not message.reply_to_message:
        tmp = await message.reply('Команда должна быть ответом на сообщение', )

        #
        await delete_message(tmp, 1)
        
        # prevent function from muting a non-existing user
        return

    # Message hasMuteReason
    if len(message.text.strip()) < 6:
        tmp = await message.answer('Нужно указать причину мьюта')
        await delete_message(message, 1)
        await delete_message(tmp, 1)
        
        # prevent function from muting a user without a reason
        return

    # set permissions to forbidden user 
    # ...

    # checking user status in current chat
    # member ojbect
    member = await bot.get_chat_member(message.chat.id, user_id)

    if member.status == 'restricted':

        # tmp = await message.answer('Пользователь уже в мьюте')

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
        except aiogram.utils.exceptions.BadRequest:

            # we skip to next chat
            continue
    

    # in_database() - is Boolean
    # if user doesn't exist (true)
    if not await in_database(user_id):

        # add him to database once
        await add_user(user_id)

    # dict to add to db
    mute_data = {
        'chat_id': message.chat.id,
        'user_id': message.reply_to_message.from_user.id,
        'message_id': message.reply_to_message.message_id,
        'moderator_message': message.text[5:],
        'admin_username': message.from_user.username
    }    

    # add mute to database
    await add_mute(mute_data)


    # delete messages   
    # tmp = await message.answer('Успешно')
    # await delete_message(tmp, 1) - sends SUCCESS


    await delete_message(message)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
    # end of mute()