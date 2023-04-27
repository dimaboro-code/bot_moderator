import os
from aiogram import Bot, Dispatcher


# init bot and dispatcher
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')

#figmachat, figmaforum, designchat2, systemchat, framerchat, whatthefontt, notionchatt, slashcomments
CHATS = [-1001302438185, -1001808148145, -1001398488197, -1001214185649, -1001124768091
         -1001753295642, -1001834470919, -1001191920744, -1001868029361]

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')


# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'


# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)

DATABASE_URL = os.getenv('DATABASE_URL') + '?sslmode=require'
