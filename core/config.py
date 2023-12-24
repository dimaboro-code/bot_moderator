"""
Как запустить локальный сервер
В терминале:  brew services start nginx
Еще в терминале: ngrok http 8080 - 8080 совпадает с портом локального сервера
После этого на страничке https://dashboard.ngrok.com/cloud-edge/endpoints откроется ссылка для вебхука
Нужна https
В настройках:
WEBHOOK_HOST = 'https://3c1c-5-76-255-147.ngrok-free.app'  # совпадает с ссылкой для вебхука (это она и есть)
WEBAPP_HOST = '127.0.0.1'  # совпадает с адресом локального сервера. можно посмотреть в nginx.conf в usr/local/etc/nginx
WEBAPP_PORT = 8080  # должен совпадать с proxypass в настройках локального сервера

Статья об этом всем: https://mkdev.me/ru/posts/ngrok-kogda-nuzhno-prokinut-vash-servis-v-internet
Если хочется еще больше поугарать - настрой SSL
"""
# python standard library
import os

# import framework
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.enums import ContentType as ct, ParseMode

# init bot and dispatcher
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


class Config:
    # CHATS = [
    #     -1001302438185,  # figmachat
    #     -1001808148145,  # figmaforum
    #     -1001398488197,  # designchat2
    #     -1001535946932,  # systemschat
    #     -1001124768091,  # framerchat
    #     -1001753295642,  # whatthefontt
    #     -1001191920744,  # slashcomments
    #     -1001769444523,  # slashimagineai
    #     -1001838011289,  # Bot Sandbox
    #     -1001629596705,  # uireview
    # ]
    #
    # LOG_CHANNEL = -1001482081082  # /designer/mutes
    CHATS = [
        -1001868029361,  # тест бота
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

    UNMUTE_SETTINGS = types.ChatPermissions(
        **{i: True for i in types.ChatPermissions.model_fields.keys()}
    )

    HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

    # webhook settings
    # WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
    WEBHOOK_HOST = 'https://3c1c-5-76-255-147.ngrok-free.app'
    # WEBHOOK_PATH = f'/webhook/{TOKEN}'
    WEBHOOK_PATH = '/webhook'

    WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

    # webserver settings
    # WEBAPP_HOST = '0.0.0.0'
    WEBAPP_HOST = '127.0.0.1'
    # WEBAPP_PORT = os.getenv('PORT', default=8000)
    WEBAPP_PORT = 8080
    # DATABASE_URL = os.getenv('DATABASE_URL')
    DATABASE_URL = 'postgresql+asyncpg://postgres:2026523@localhost:5432/postgres'
    WEBHOOK_SECRET = 'jadhkjs745623hdfh'
