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
import asyncio
import os

import httpx
from aiogram import types
from aiogram.enums import ContentType


async def get_ngrok_url(ngrok_api_url, max_retries=10, delay=5):
    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            try:
                response = await client.get(ngrok_api_url)
                response.raise_for_status()
                data = response.json()
                public_url = data['tunnels'][0]['public_url']
                print(f"Ngrok public URL: {public_url}")
                return public_url
            except httpx.RequestError as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                await asyncio.sleep(delay)
        raise Exception("Failed to get ngrok URL after multiple attempts")


class ProdConfig:
    # Настройки для прода
    CHATS = (
        -1001398488197,  # designchat2
        -1001302438185,  # figmachat
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
    MESSAGE_CONTAINER_CHAT: int = -1002455952036  # for strict mode

    HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
    WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
    WEBAPP_HOST = os.getenv('WEBAPP_HOST', default='0.0.0.0')
    WEBAPP_PORT = int(os.getenv('WEBAPP_PORT', default=8000))
    DATABASE_URL = os.getenv('DATABASE_URL', '')  # Основная бд
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

    # webhook settings
    WEBHOOK_PATH = '/webhook'
    WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'


class DevConfig:
    # настройки для тестов
    from dotenv import load_dotenv
    env = load_dotenv(dotenv_path='./dev.env')
    if not env:
        print('.env файл не найден')

    CHATS = (
        -1001868029361,  # тест бота
    )
    ngrok_api_url = os.getenv('NGROK_API_URL', 'http://ngrok/api/tunnels')
    LOG_CHANNEL: int = os.getenv('LOG_CHANNEL', -1002065542994)
    BOT_USERNAME: str = 'testing_projects_42_bot'  # telegram
    LOG_CHAT: int = os.getenv('LOG_CHAT', -1001868029361)  # for mistakes, db
    MESSAGE_CONTAINER_CHAT: int = -4549380236  # db
    WEBHOOK_HOST = asyncio.run(get_ngrok_url(ngrok_api_url))
    WEBAPP_HOST = os.getenv("WEBAPP_HOST")
    WEBAPP_PORT = int(os.getenv("WEBAPP_PORT"))

    # webhook settings
    WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', default='/webhook')
    WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

    DATABASE_URL = 'postgresql+asyncpg://postgres:2026523@localhost:5432/postgres'  # для тестов, локальная


def get_settings():
    '''
    для хероку
    Returns:

    '''
    dev_settings = bool(os.getenv('SET_DEV_SETTINGS', False))
    if dev_settings:
        return DevConfig
    return ProdConfig


class ConfigVars(get_settings()):
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
        ContentType.GENERAL_FORUM_TOPIC_UNHIDDEN,
    )

    MUTE_SETTINGS: types.ChatPermissions = types.ChatPermissions(
        **{i: False for i in types.ChatPermissions.model_fields.keys()}
    )
    UNMUTE_SETTINGS = types.ChatPermissions(
        **{i: True for i in types.ChatPermissions.model_fields.keys()}
    )

    # webserver settings
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
    REDIS_URL = os.getenv('REDIS_URL')
