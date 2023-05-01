import asyncio
import logging
from contextlib import suppress

import aiogram.utils.exceptions
from aiogram.utils.exceptions import (MessageCantBeDeleted, MessageToDeleteNotFound)
from aiogram.utils.executor import start_webhook, start_polling
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from config import bot, dp, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, LOG_CHANNEL_ID, CHATS
from db import *
from cleaner import messages_for_delete


# Configure logging
logging.basicConfig(level=logging.INFO)


# webhook control
async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await database.connect()


async def on_shutdown(dispatcher):
    await database.disconnect()
    await bot.delete_webhook()


# help_functions
async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


@dp.message_handler(commands=['delete_user'])
async def delete_user(message: types.Message):
    await delete_row(message.from_user.id)


async def restrict(user, chat, hummer):
    try:
        member = await bot.get_chat_member(chat, user)
        if not member.is_chat_member():
            return
    except aiogram.exceptions.BadRequest:
        return
    await bot.restrict_chat_member(
        chat_id=chat,
        user_id=user,
        permissions=hummer,
        until_date=10
    )


# private chat functions



@dp.message_handler(commands=['start'], chat_type='private')
async def send_welcome(message: types.Message):
    hello_message = (
        f'Привет!\n\n'
        f'Раз ты тут, то, наверное, тебя лишили голоса (замьютили) в чатах проекта @slashdesigner. '
        f'Мьют в одном чате действует во всех наших чатах сразу.\n'
        f'Я помогу тебе разблокироваться, только прочитай перед этим наши правила, '
        f'чтобы избежать новых блокировок в будущем.\n\n'
        f'@figmachat        <a href="https://slashdesigner.ru/figmachat/rules">Правила</a>\n'
        f'@designchat2     <a href="https://slashdesigner.ru/designchat/rules">Правила</a>\n'
        f'@whatthefontt    <a href="https://slashdesigner.ru/whatthefont/rules">Правила</a>\n'
        f'@systemschat     <a href="http://slashd.ru/systemschat/rules">Правила</a>\n\n'
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
        await message.answer('Здравствуйте!\n Вы не блокировались ботом.')
        return
    last_mute = await get_last_mute(user_id)
    user_data = await get_user(user_id)
    chat = await bot.get_chat(last_mute["chat_id"])
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


@dp.message_handler(chat_type='private', commands=['unmute'], commands_prefix='!/')
async def unmute(message: types.Message):
    user_id = message.from_user.id

    if not await in_database(user_id):
        await message.answer('Вы вне системы. Совершите противоправное действие, чтобы стать частью')
        return

    last_mute = await get_last_mute(user_id)
    user_data = await get_user(user_id)
    print(last_mute['chat_id'], user_id, last_mute['user_id'])
    # для получения инфы о пользователе нужно быть админом группы
    try:
        member = await bot.get_chat_member(chat_id=last_mute['chat_id'], user_id=user_id)
        print(member)
        if member.can_send_messages is True:
            await message.answer('Вы уже разблокированы. Если это не так, обратитесь в поддержку.')
            return
    except aiogram.exceptions.BadRequest:
        pass
    if user_data['user_blocks'] > 0:
        await db_unmute(user_id)

        unmute_hammer = types.ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_send_polls=True,
            can_add_web_page_previews=True
        )
        for chat in CHATS:
            await restrict(user_id, chat, unmute_hammer)
        await status(message)
    else:
        await message.answer('У Вас закончились разблоки.')


# group chat functions
@dp.message_handler(commands=['mute'], is_chat_admin=True, commands_prefix='!/')
async def mute(message: types.Message):

    user_id = message.reply_to_message.from_user.id
    # checking form to be right
    if not message.reply_to_message:
        tmp = await message.reply('Команда должна быть ответом на сообщение!', )
        await delete_message(tmp, 1)

    if len(message.text.strip()) < 6:
        tmp = await message.answer('Нужно указать причину мьюта')
        await delete_message(message, 1)
        await delete_message(tmp, 1)

    # data added to db
    mute_data = {
        'chat_id': message.chat.id,
        'user_id': message.reply_to_message.from_user.id,
        'message_id': message.reply_to_message.message_id,
        'moderator_message': message.text[5:],
        'admin_username': message.from_user.username
    }

    # add user to database
    if not await in_database(mute_data['user_id']):
        await add_user(message.reply_to_message.from_user.id)

    # set permissions to forbidden
    mute_hummer = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False
    )
    # change permissions
    for chat in CHATS:
        try:
            member = await bot.get_chat_member(chat, user_id)
        except aiogram.utils.exceptions.BadRequest:
            continue
        await restrict(user_id, chat, mute_hummer)
    tmp = await message.answer('Успешно')

    # add mute to database
    await add_mute(mute_data)

    # delete messages
    await delete_message(tmp, 1)
    await delete_message(message)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)


@dp.message_handler(commands=['add_unblocks'],  is_chat_admin=True, commands_prefix='!/')
async def add_unblocks(message: types.Message):
    user_id = message.reply_to_message.from_user.id
    lives = int(message.text[14:]) if len(str(message.text)) >= 15 else 1
    await add_lives(user_id, lives)
    await message.delete()


@dp.message_handler(commands=['ban'],  is_chat_admin=True, commands_prefix='!/')
async def ban(message: types.Message):
    if not message.reply_to_message:
        tmp = await message.reply('Команда должна быть ответом на сообщение!', )
        await delete_message(tmp, 10)
    await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    text = '{} c айди {} забанен в чате {} за {} админом {}'.format(
        message.reply_to_message.from_user.username,
        message.reply_to_message.from_user.id,
        message.chat.id,
        message.text[5:],
        message.from_user.username
    )
    await bot.send_message(chat_id=LOG_CHANNEL_ID, text=text)
    tmp = await message.answer(f'User {message.reply_to_message.from_user.username} is banned')
    asyncio.create_task(delete_message(tmp, 5))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)


@dp.message_handler(commands=['unban'], commands_prefix='!/')
async def unban(message: types.Message):
    '''
    в чате после команды через пробел пишется чат айди и юзер айди
    :param message:
    :return:
    '''
    cmd, chat_id, user_id = str(message.text).strip().split(' ')
    await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
    tmp = await message.answer('Разбанен')
    asyncio.create_task(delete_message(tmp, 10))


@dp.message_handler(content_types=messages_for_delete)
async def delete_messages(message: types.Message):
    await message.delete()


# async def startup(dp):
#     await database.connect()
#
#
# async def shutdown(dp):
#     await database.disconnect()


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
