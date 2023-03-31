import asyncio
import logging
import os
from contextlib import suppress
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import (MessageCantBeDeleted, MessageToDeleteNotFound)
from aiogram.utils.executor import start_webhook
from aiogram import Bot, types
from databases import Database
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize vars
TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
DATABASE_URL = os.getenv('DATABASE_URL')

# Initialize bot, database and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
database = Database(DATABASE_URL)

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)


# webhook control
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await database.connect()

async def on_shutdown():
    await database.disconnect()
    await bot.delete_webhook()


# help_functions
async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()

# database functions
async def in_database(user_id):
    results = await database.fetch_all(f'SELECT * FROM users '
                                       f'WHERE user_id = :user_id ',
                                       values={'user_id': user_id})
    return bool(len(results))

async def add_user(message: types.Message):
    date = str(datetime.datetime.now())[:19]
    await database.execute(f'INSERT INTO users (user_id, date_add) '
                           f'VALUES (:user_id, :date_add)',
                           values={'user_id': message.reply_to_message.from_user.id,
                                   'date_add': date})

async def add_mute(mute_data):
    await database.execute(f'INSERT INTO mutes (user_id, message_id, chat_id, '
                           f'moderator_message, date_of_mute, admin_username) '
                           f'VALUES (:user_id, :message_id, :chat_id, '
                           f':moderator_message, :date_of_mute, :admin_username)',
                           values=mute_data)
    user_id = mute_data['user_id']
    lives = await database.fetch_one(f'SELECT user_blocks FROM users WHERE user_id = :user_id',
                             values={'user_id': user_id})
    await database.execute(f'UPDATE users SET (user_block = :user_block, is_muted = :is_muted)'
                           f'WHERE user_id = :user_id',
                           values={'user_blocks': int(lives) - 1, 'user_id': user_id, 'is_muted': 'TRUE'})

async def remove_from_mute(user_id):
    results = await database.fetch_all(
        f'SELECT * FROM mutes WHERE user_id = :user_id AND date_of_mute = ('
        f'SELECT MAX (date_of_mute) FROM mutes WHERE user_id = :user_id)',
        values={'user_id': user_id}
    )
    user_data = [next(result.values()) for result in results]
    return user_data

# private chat functions
@dp.message_handler(commands=['start', 'help'], chat_type='private')
async def send_welcome(message: types.Message):
    await message.answer(f'Hello, {message.from_user.first_name}')


@dp.message_handler(chat_type='private', commands=['unmute'], commands_prefix='!/')
async def unmute(message: types.Message):
    user_id = message.from_user.id

    if not in_database(user_id):
        return message.answer('Вы вне системы. Совершите противоправное действие, чтобы присоединиться')

    user_data = await remove_from_mute(user_id)
    await message.answer(user_data)

    unmute_hammer = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )
    await bot.restrict_chat_member(
        message.text[8:],  # chat id
        user_id,
        permissions=unmute_hammer
    )
    await message.answer('done')


# group chat functions
@dp.message_handler(commands=['mute'], is_chat_admin=True, commands_prefix='!/')
async def mute(message: types.Message):
    # checking form to be right
    if not message.reply_to_message:
        tmp = await message.reply('Команда должна быть ответом на сообщение!', )
        asyncio.create_task(delete_message(tmp, 10))

    # data added to db
    mute_data = {
        'chat_id': message.chat.id,
        'user_id': message.reply_to_message.from_user.id,
        'message_id': message.reply_to_message.message_id,
        'moderator_message': message.text[5:],
        'date_on_mute': str(datetime.datetime.now()[:18]),
        'admin_username': message.from_user.username
    }
    # add user to database
    if not in_database(mute_data['user_id']):
        await add_user(message)
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
        permissions=mute_hummer
    )
    tmp = await message.answer(message.chat.id)
    asyncio.create_task(delete_message(tmp, 10))
    await message.delete()


# delete messages about join and left group

messages_for_delete = [
    'new_chat_members',
    'left_chat_member',
    'delete_chat_photo',
    'delete_chat_sticker_set',
    'delete_chat_title',
    'pinned_message',
    'unpinned_message',
    'new_chat_title',
    'new_chat_description',
]


@dp.message_handler(content_types=messages_for_delete)
async def delete_messages(message: types.Message):
    await message.delete()


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
