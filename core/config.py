# python standard library
import os

# import framework
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.enums import ContentType as ct

# init bot and dispatcher
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()


class Config:

    CHATS = [
        -1001868029361,    # тест бота
    ]

    LOG_CHANNEL = -1002065542994

    MESSAGES_FOR_DELETE = [
        ct.NEW_CHAT_MEMBERS,
        ct.LEFT_CHAT_MEMBER,
        ct.NEW_CHAT_PHOTO,
        ct.DELETE_CHAT_PHOTO,
        'delete_chat_sticker_set',
        ct.NEW_CHAT_TITLE,
        'delete_chat_title',
        ct.GROUP_CHAT_CREATED,
        ct.SUPERGROUP_CHAT_CREATED,
        ct.CHANNEL_CHAT_CREATED,
        ct.MESSAGE_AUTO_DELETE_TIMER_CHANGED,
        ct.PINNED_MESSAGE,
        'unpinned_message',
        'new_chat_description',
        ct.VIDEO_CHAT_SCHEDULED,
        ct.VIDEO_CHAT_STARTED,
        ct.VIDEO_CHAT_ENDED,
        ct.VIDEO_CHAT_PARTICIPANTS_INVITED,
        ct.FORUM_TOPIC_CREATED,
        ct.FORUM_TOPIC_EDITED,
        ct.FORUM_TOPIC_CLOSED,
        ct.FORUM_TOPIC_REOPENED,
        ct.GENERAL_FORUM_TOPIC_HIDDEN,
        ct.GENERAL_FORUM_TOPIC_UNHIDDEN
    ]

    # Чтобы не прописывать руками все разрешения, я достаю их из объекта, в генераторе
    # словаря прописываю соответствия и затем распечатываю словарь в нужную мне форму
    MUTE_SETTINGS: types.ChatPermissions = types.ChatPermissions(
        **{i: False for i in types.ChatPermissions.model_fields.keys()}
    )

    ADMINS = []

    UNMUTE_SETTINGS = types.ChatPermissions(
        **{i: True for i in types.ChatPermissions.model_fields.keys()}
    )

    # HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

    # webhook settings
    # WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
    # WEBHOOK_PATH = f'/webhook/{TOKEN}'
    # WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

    # webserver settings
    # WEBAPP_HOST = '0.0.0.0'
    # WEBAPP_PORT = os.getenv('PORT', default=8000)

    DATABASE_URL = 'postgresql+asyncpg://postgres:2026523@localhost:5432/postgres'
