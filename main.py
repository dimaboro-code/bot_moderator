import asyncio
import logging
from contextlib import suppress
from aiogram.utils.exceptions import (MessageCantBeDeleted, MessageToDeleteNotFound)
from aiogram.utils.executor import start_webhook, start_polling
from aiogram import types
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


# private chat functions
@dp.message_handler(commands=['start'], chat_type='private')
async def send_welcome(message: types.Message):
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
    last_mute, user_data = await get_user_data(user_id=user_id)
    chat = await bot.get_chat(last_mute["chat_id"])
    reason_to_mute = await bot.get_message(chat_id=last_mute["chat_id"], message_id=last_mute["message_id"])
    answer = (f'Статус\n'
 
              f'Текущее состояние: {("разблокирован", "заблокирован")[user_data["is_muted"]]}\n' 
              f'Осталось разблокировок: {user_data["user_blocks"]}\n\n' 
              f'Последний мьют\n' 
              f'Причина: {last_mute["moderator_message"]}\n' 
              f'Чат: {chat.username}\n' 
              f'Админ: {last_mute["admin_username"]}\n' 
              f'Сообщение: {reason_to_mute.text}\n' 
              f'Дата мьюта: {last_mute["date_of_mute"]}')
    await delete_message(reason_to_mute)
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
    username = message.text[9:]
    chat = await bot.get_chat(username)
    await message.answer(chat.id)


@dp.message_handler(chat_type='private', commands=['unmute'], commands_prefix='!/')
async def unmute(message: types.Message):
    user_id = message.from_user.id

    if not await in_database(user_id):
        await message.answer('Вы вне системы. Совершите противоправное действие, чтобы стать частью')
        return

    user_data = await get_user_data(user_id)
    last_mute = user_data[0]
    user_data = user_data[1]
    member = await bot.get_chat_member(chat_id=last_mute['chat_id'], user_id=user_id)
    if member.can_send_messages:
        await message.answer('Вы уже разблокированы. Если это не так, обратитесь в поддержку.')
        return
    if user_data['user_blocks'] >= 0:
        await db_unmute()

        unmute_hammer = types.ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        await bot.restrict_chat_member(
            last_mute['chat_id'],
            user_data['user_id'],
            permissions=unmute_hammer
        )
        await status(message)
    else:
        await message.answer('У Вас закончились разблоки. Ожидайте, когда Дима напишет нужный функционал.')


# group chat functions
@dp.message_handler(commands=['mute'], is_chat_admin=True, commands_prefix='!/')
async def mute(message: types.Message):
    # checking form to be right
    if not message.reply_to_message:
        tmp = await message.reply('Команда должна быть ответом на сообщение!', )
        await delete_message(tmp, 5)

    if len(message.text.strip()) < 6:
        await message.answer('Нужно указать причину мьюта')
        await delete_message(message, 5)

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
    # add mute to database
    await add_mute(mute_data)

    # set permissions to forbidden
    mute_hummer = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False
    )
    # change permissions
    await bot.restrict_chat_member(
        message.chat.id,
        message.reply_to_message.from_user.id,
        permissions=mute_hummer, 
        until_date=10
    )
    tmp = await message.answer('Успешно')
    await delete_message(tmp, 5)
    await delete_message(message, 5)


@dp.message_handler(commands=['add_unblocks'],  is_chat_admin=True, commands_prefix='!/')
async def add_unblocks(message: types.Message):
    user_id = message.reply_to_message.from_user.id
    lifes = int(message.text[14:]) if len(str(message.text)) == 15 else 1
    await add_lifes(user_id, lifes)
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
