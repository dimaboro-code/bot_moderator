import logging
import config
from db import Database

from aiogram import Bot, Dispatcher, executor, types

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
db = Database('database.db')
bot = Bot(token=config.token)
dp = Dispatcher(bot)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

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
    await message.answer(f'Hello, {message.from_user.first_name}')


@dp.message_handler(commands=['mute'], is_chat_admin=True)
async def mute(message: types.Message):
    if not message.reply_to_message:
        await message.reply('Команда должна быть ответом на сообщение!')

    user_message = message.reply_to_message
    user_id = message.reply_to_message.from_user.id
    user_username = message.reply_to_message.from_user.username
    moderator_username = message.from_user.username
    db.add_mute(user_id)
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
    await message.answer('muted')


@dp.message_handler(commands=['unmute'], is_chat_admin=True)
async def mute(message: types.Message):
    user_message = message.reply_to_message
    if not message.reply_to_message:
        await message.reply('Команда должна быть ответом на сообщение!')

    user_id = message.reply_to_message.from_user.id
    new = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )
    await bot.restrict_chat_member(
        message.chat.id,
        user_message.from_user.id,
        permissions=new
    )
    db.unmute(user_id)
    await message.answer('done')


# delete messages about join and left group
@dp.message_handler(content_types=['new_chat_members', 'left_chat_member'])
async def new_chat(message: types.Message):
    await message.delete()

@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    if not db.exist_user(message.from_user.id):
        db.add(message.from_user.id)
    if not db.mute(message.from_user.id):
        print(db.mute(message.from_user.id))
    else:
        await message.delete()

if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=True)