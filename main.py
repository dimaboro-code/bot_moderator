import logging
import os
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram import Bot, types

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize vars
TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(f'Hello, {message.from_user.first_name}\n {message}')


@dp.message_handler(commands=['mute'], is_chat_admin=True)
async def mute(message: types.Message):
    if not message.reply_to_message:
        await message.reply('Команда должна быть ответом на сообщение!')

    user_message = message.reply_to_message
    # user_id = message.reply_to_message.from_user.id
    # user_username = message.reply_to_message.from_user.username
    # moderator_username = message.from_user.username
    # db.add_mute(user_id)
    new = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False
    )
    await bot.restrict_chat_member(
        message.chat.id,
        user_message.from_user.id,
        permissions=new
    )
    await message.answer(message.chat.id)


@dp.message_handler(chat_type=['is_private'], commands=['unmute'])
async def unmute(message: types.Message):
    
    user_id = message.from_user.id
    new = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )
    await bot.restrict_chat_member(
        message.text[8:],  # chat id
        message.from_user.id,
        permissions=new
    )
    await message.answer('done')


# delete messages about join and left group
@dp.message_handler(content_types=['new_chat_members', 'left_chat_member'])
async def new_chat(message: types.Message):
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
