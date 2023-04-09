import asyncio
import logging
from contextlib import suppress
from aiogram.utils.exceptions import (MessageCantBeDeleted, MessageToDeleteNotFound)
from aiogram.utils.executor import start_webhook, start_polling
from aiogram import types
from config import bot, dp, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from db import database, in_database, add_mute, add_user, remove_from_mute
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


# database functions
@dp.message_handler(commands=['in_database'])
async def in_database(message: types.Message):
    user_id = message.from_user.id
    results = await database.fetch_all(f'SELECT * FROM users '
                                       f'WHERE user_id = :user_id',
                                       values={'user_id': user_id})
    logging.info(bool(len(results)))
    return bool(len(results))


# private chat functions
@dp.message_handler(commands=['start', 'help'], chat_type='private')
async def send_welcome(message: types.Message):
    await message.answer(f'Hello, {message.from_user.first_name}')


@dp.message_handler(chat_type='private', commands=['unmute'], commands_prefix='!/')
async def unmute(message: types.Message):
    user_id = message.from_user.id

    if not await in_database(message):
        return await message.answer('Вы вне системы. Совершите противоправное действие, чтобы стать частью')

    user_data = await remove_from_mute(user_id)
    await message.answer(str(user_data))

    unmute_hammer = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )
    await bot.restrict_chat_member(
        -1001868029361,
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
        'admin_username': message.from_user.username
    }
    # add user to database
    if not in_database(mute_data['user_id']):
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
        permissions=mute_hummer
    )
    tmp = await message.answer(message.chat.id)
    asyncio.create_task(delete_message(tmp, 10))
    await message.delete()


@dp.message_handler(content_types=messages_for_delete)
async def delete_messages(message: types.Message):
    await message.delete()


# if __name__ == '__main__':
#     start_polling(dp, skip_updates=True)
    # start_webhook(
    #     dispatcher=dp,
    #     webhook_path=WEBHOOK_PATH,
    #     skip_updates=True,
    #     on_startup=on_startup,
    #     on_shutdown=on_shutdown,
    #     host=WEBAPP_HOST,
    #     port=WEBAPP_PORT,
    # )
