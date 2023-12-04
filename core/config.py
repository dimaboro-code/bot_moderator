# python standard library
import os

# import framework
from aiogram import Bot, Dispatcher


from aiogram import types

# init bot and dispatcher
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

CHATS = [

    -1001868029361,    # тест бота
]

LOG_CHANNEL = -1002065542994

MESSAGES_FOR_DELETE = [
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

# Чтобы не прописывать руками все разрешения, я достаю их из объекта, в генераторе
# словаря прописываю соответствия и затем распечатываю словарь в нужную мне форму
MUTE_SETTINGS: types.ChatPermissions = types.ChatPermissions(
    **{i: False for i in types.ChatPermissions().values.keys()}
)


UNMUTE_SETTINGS = types.ChatPermissions(
    **{i: True for i in types.ChatPermissions().values.keys()}
)

# HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')


# webhook settings
# WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
# WEBHOOK_PATH = f'/webhook/{TOKEN}'
# WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'


# webserver settings
# WEBAPP_HOST = '0.0.0.0'
# WEBAPP_PORT = os.getenv('PORT', default=8000)

DATABASE_URL = 'postgresql+asyncpg://postgres:2026523@localhost:5432/postgres' + '?sslmode=require'
