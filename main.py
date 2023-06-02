
# direct import of async lib IO
# it is needed for delete_message()
import asyncio

# types – our object models, like Message or Chat
from aiogram import types

# all actions logger, currently doesn't exist
import logging

# helper for delete_message()
from contextlib import suppress

import aiogram.utils.exceptions

# defines exceptions for delete_message()
from aiogram.utils.exceptions import (MessageCantBeDeleted, MessageToDeleteNotFound)

# run webhook
from aiogram.utils.executor import start_webhook

# settings import
from config import bot, dp, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, CHATS, MESSAGES_FOR_DELETE, MUTE_SETTINGS, UNMUTE_SETTINGS

# full database import
from db import *

from group_functions.mute import mute


# Configure logging
logging.basicConfig(level=logging.INFO)

# webhook control
async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await database.connect()

# stopping app
async def on_shutdown(dispatcher):
    await database.disconnect()
    await bot.delete_webhook()


#mute
dp.register_message_handler(mute, commands=['mute'], is_chat_admin=True, commands_prefix='!/')



# DELETE MESSAGE

async def delete_message(message: types.Message, sleep_time: int = 0):

    # message removal after delay
    await asyncio.sleep(sleep_time)

    # error handling, which avoide try-except block
    # handling exception messages.

    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


@dp.message_handler(commands=['delete_user'])

async def delete_user(message: types.Message):
    await delete_row(message.from_user.id)


# MUTER
async def restrict(user_id, chat_id, permissions):

    # mute action
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        
        # permissions = default parameter name
        permissions=permissions,

        # mute time, if < 30 = forever
        until_date=10
    )

# GROUP CHAT FUNCTIONS

# 1. MUTE

# mute - symbol combination from chat


async def mute(message: types.Message):
    await message.answer("mute")

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

        tmp = await message.answer('Пользователь уже в мьюте')

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


        # if we catch bad request when user_id is not found
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


#ADD UNBLOCKS

@dp.message_handler(commands=['add_unblocks'],  is_chat_admin=True, commands_prefix='!/')

async def add_unblocks(message: types.Message):
    user_id = message.reply_to_message.from_user.id
    lives = int(message.text[14:]) if len(str(message.text)) >= 15 else 1
    await add_lives(user_id, lives)
    await message.delete()


# JOIN CLEANER

@dp.message_handler(content_types=MESSAGES_FOR_DELETE)
async def delete_messages(message: types.Message):
    await message.delete()


# PRIVATE CHAT FUNCTIONS 


# /start

@dp.message_handler(commands=['start'], chat_type='private')
async def send_welcome(message: types.Message):
    hello_message = (
        f'Привет!\n\n'
        f'Раз ты тут, то, наверное, тебя лишили голоса (замьютили) в чатах проекта @slashdesigner. '
        f'Мьют в одном чате действует во всех наших чатах сразу.\n'
        f'Я помогу тебе разблокироваться, только прочитай перед этим наши правила, '
        f'чтобы избежать новых блокировок в будущем.\n\n'
        f'@figmachat        <a href="https://slashdesigner.ru/figmachat">Правила</a>\n'
        f'@designchat2     <a href="https://slashdesigner.ru/designchat">Правила</a>\n'
        f'@whatthefontt    <a href="https://slashdesigner.ru/whatthefont">Правила</a>\n'
        f'@systemschat     <a href="http://slashd.ru/systemschat">Правила</a>\n\n'
        f'У каждого участника чатов есть 3 разблока — возможности вернуть голос во всех чатах. '
        f'После третьего мьюта нам придётся навсегда оставить тебя в режиме читателя.'
    )
    await message.answer(hello_message, parse_mode='HTML', disable_web_page_preview=True)
    await bot_help(message)
    await status(message)


@dp.message_handler(commands=['status'], chat_type='private')
async def status(message: types.Message):
    ''' start func
    :param message:
    :return:
    '''
    user_id = message.from_user.id

    is_in_database = await in_database(user_id=user_id)

    if not is_in_database:
        await message.answer('Статус: У вас осталось 3 разблока.')
        return None

    last_mute = await get_last_mute(user_id)

    if last_mute is None:
        await message.answer('Нет данных о мьюте')
    else:
        chat = await bot.get_chat(last_mute["chat_id"])

    user_data = await get_user(user_id)

    # reason_to_mute = await bot.get_message(chat_id=last_mute["chat_id"], message_id=last_mute["message_id"])
    answer = (f'Статус\n'
 
              f'Текущее состояние: {("разблокирован", "заблокирован")[user_data["is_muted"]]}\n' 
              f'Осталось разблокировок: {user_data["user_blocks"]}\n\n' 
              f'Последний мьют\n'
              f'Причина: {last_mute["moderator_message"]}\n' 
              f'Чат: {chat.username}\n' 
              f'Админ: {last_mute["admin_username"]}\n' 
              # f'Сообщение: {reason_to_mute.text}\n' 
              f'Дата мьюта: {last_mute["date_of_mute"]}')
    # await delete_message(reason_to_mute)
    await message.answer(answer)


@dp.message_handler(commands=['help'], chat_type='private', state='*')
async def bot_help(message: types.Message):
    """
    :param message:
    :return:
    """
    text = 'Доступные команды\n\n'
    text += '/start - запустить бота\n'
    text += '/unmute - разблокироваться\n'
    text += '/help - список доступных команд\n'
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['chat_id'], chat_type='private')
async def get_chat_id(message: types.Message):
    chat_ids = []
    text = message.text.strip().split()
    text.pop(0)
    answer = None
    for chat in text:
        print(chat)
        chat_id = await bot.get_chat(chat)
        chat_ids.append(str(chat_id.id))
        answer = ' '.join(chat_ids)
    await message.answer(answer)


# UNMUTE

@dp.message_handler(chat_type='private', commands=['unmute'], commands_prefix='!/')
async def unmute(message: types.Message):
    user_id = message.from_user.id

    if not await in_database(user_id):
        await message.answer('Вы вне системы. Совершите противоправное действие, чтобы стать частью')
        return

    last_mute = await get_last_mute(user_id)
    user_data = await get_user(user_id)
 
    # для получения инфы о пользователе нужно быть админом группы
    try:
        member = await bot.get_chat_member(chat_id=last_mute['chat_id'], user_id=user_id)
        print(member)
        if member.can_send_messages is True:
            await message.answer('Вы уже разблокированы. Если это не так, обратитесь в поддержку.')
            return
    except AttributeError:
        pass
    if user_data['user_blocks'] > 0:
        await db_unmute(user_id)



        for chat in CHATS:
            await restrict(user_id, chat, UNMUTE_SETTINGS)
        await status(message)
    else:
        await message.answer('У вас закончились разблоки.')


if __name__ == '__main__':

    # start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
