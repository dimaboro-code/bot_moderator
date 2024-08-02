"""
Как запустить локальный сервер.

В терминале:  brew services start nginx - можно не использовать, если нгрок запустить на порте вебапп
Еще в терминале: ngrok http 8080 - 8080 совпадает с портом локального сервера
После этого на страничке https://dashboard.ngrok.com/cloud-edge/endpoints откроется ссылка для вебхука
Нужна https
В настройках:
WEBHOOK_HOST = 'https://3c1c-5-76-255-147.ngrok-free.app'  # совпадает с ссылкой для вебхука (это она и есть)
WEBAPP_HOST = '127.0.0.1'  # совпадает с адресом локального сервера. можно посмотреть в nginx.conf в usr/local/etc/nginx
WEBAPP_PORT = 8080  # должен совпадать с proxypass в настройках локального сервера

Статья об этом всем: https://mkdev.me/ru/posts/ngrok-kogda-nuzhno-prokinut-vash-servis-v-internet
Если хочется еще больше поугарать - настрой SSL.
"""

import os

from aiogram import types
from aiogram.enums import ContentType


class ProdConfig:
    # Настройки для прода
    CHATS = (
        -1001302438185,  # figmachat
        -1001808148145,  # figmaforum
        -1001398488197,  # designchat2
        -1001535946932,  # systemschat
        -1001124768091,  # framerchat
        -1001753295642,  # whatthefontt
        -1001191920744,  # slashcomments
        -1001769444523,  # slashimagineai
        -1001838011289,  # Bot Sandbox
        -1001629596705,  # uireview
    )
    LOG_CHANNEL: int = -1001482081082  # /designer/mutes
    BOT_USERNAME: str = 'slashdbot'
    LOG_CHAT: int = -1001838011289  # for mistakes

    HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
    WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
    WEBAPP_HOST = '0.0.0.0'
    WEBAPP_PORT = int(os.getenv('PORT', default=8000))
    DATABASE_URL = os.getenv('DATABASE_URL_TRUE')  # Основная бд

    # webhook settings
    WEBHOOK_PATH = '/webhook'
    WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'


class DevConfig:
    # настройки для тестов
    from dotenv import load_dotenv
    env = load_dotenv()
    if not env:
        print('.env файл не найден')

    CHATS = (
        -1001868029361,  # тест бота
    )

    LOG_CHANNEL: int = -1002065542994
    BOT_USERNAME: str = 'testing_projects_42_bot'
    LOG_CHAT: int = -1001868029361  # for mistakes

    WEBHOOK_HOST = 'https://b4e2-178-88-32-157.ngrok-free.app'
    WEBAPP_HOST = '127.0.0.1'
    WEBAPP_PORT = 8080

    # webhook settings
    WEBHOOK_PATH = '/webhook'
    WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

    DATABASE_URL = 'postgresql+asyncpg://postgres:2026523@localhost:5432/postgres'  # для тестов, локальная


class ConfigVars(DevConfig):
    # Общие настройки
    TOKEN = os.getenv('BOT_TOKEN')  # Боты разные, но значение в обоих случаях берется из ENV

    MESSAGES_FOR_DELETE = (
        ContentType.NEW_CHAT_MEMBERS,
        ContentType.LEFT_CHAT_MEMBER,
        ContentType.NEW_CHAT_PHOTO,
        ContentType.DELETE_CHAT_PHOTO,
        'delete_chat_sticker_set',
        ContentType.NEW_CHAT_TITLE,
        'delete_chat_title',
        ContentType.GROUP_CHAT_CREATED,
        ContentType.SUPERGROUP_CHAT_CREATED,
        ContentType.CHANNEL_CHAT_CREATED,
        ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED,
        ContentType.PINNED_MESSAGE,
        'unpinned_message',
        'new_chat_description',
        ContentType.VIDEO_CHAT_SCHEDULED,
        ContentType.VIDEO_CHAT_STARTED,
        ContentType.VIDEO_CHAT_ENDED,
        ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
        ContentType.FORUM_TOPIC_CREATED,
        ContentType.FORUM_TOPIC_EDITED,
        ContentType.FORUM_TOPIC_CLOSED,
        ContentType.FORUM_TOPIC_REOPENED,
        ContentType.GENERAL_FORUM_TOPIC_HIDDEN,
        ContentType.GENERAL_FORUM_TOPIC_UNHIDDEN
    )

    MUTE_SETTINGS: types.ChatPermissions = types.ChatPermissions(
        **{i: False for i in types.ChatPermissions.model_fields.keys()}
    )
    UNMUTE_SETTINGS = types.ChatPermissions(
        **{i: True for i in types.ChatPermissions.model_fields.keys()}
    )

    # webserver settings
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
