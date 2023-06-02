import os
from aiogram import Bot, Dispatcher, types


# init bot and dispatcher
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
DATABASE_URL = 'postgresql+asyncpg://postgres:2026523@localhost:5432/postgres'
#figmachat, figmaforum, designchat2, systemschat, framerchat, whatthefontt, slashcomments
# тест бота
# CHATS = [
#     -1001302438185,
#     -1001808148145,
#     -1001398488197,
#     -1001535946932,
#     -1001124768091,
#     -1001753295642,
#     -1001191920744
# ]
CHATS = [-1001868029361]


# set permissions to forbidden
mute_hammer = types.ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False
)

unmute_hammer = types.ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_send_polls=True,
    can_add_web_page_previews=True

)