# os
import os

# import framework
from aiogram import Bot, Dispatcher

from aiogram import types

# init bot and dispatcher
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

CHATS = [
    -1001302438185,  # figmachat
    -1001808148145,  # figmaforum
    -1001398488197,  # designchat2
    -1001535946932,  # systemschat
    -1001124768091,  # framerchat
    -1001753295642,  # whatthefontt
    -1001191920744,  # slashcomments 
    -1001769444523   # slashimagineai
]

# CHATS = [-1001868029361] тестовый чат

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

MUTE_SETTINGS = types.ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
)



UNMUTE_SETTINGS = types.ChatPermissions(
    can_send_messages=True,

    # photo, video, stickers
    can_send_media_messages=True,

    # files
    can_send_other_messages=True,
    
    can_send_polls=True,

    # links
    can_add_web_page_previews=True
)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')


# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'


# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)

DATABASE_URL = os.getenv('DATABASE_URL') + '?sslmode=require'
