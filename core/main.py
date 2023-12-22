# all actions logger, currently doesn't exist
import asyncio
import logging
from typing import List

# run webhook
from aiogram import F
from aiogram.filters import Command, CommandStart

# settings import
from core.config import bot, dp, Config
# full database import
from core.database_functions.db_functions import async_main
from core.handlers.callback_privatechat_functions.callback_show_users import show_user_react
# GROUP FUNCTION IMPORTS
from core.handlers.group_functions.add_unblocks import add_unblocks
from core.handlers.group_functions.id_recognizer import know_id
from core.handlers.group_functions.join_cleaner import join_cleaner
from core.handlers.group_functions.mute_main import mute
from core.handlers.privatechat_functions.bot_help import bot_help
# SYSTEM FUNCTION IMPORTS
from core.handlers.privatechat_functions.eraser import eraser
from core.handlers.privatechat_functions.get_chat_id import get_chat_id
from core.handlers.privatechat_functions.send_report import send_report
# PRIVATECHAT FUNCTION IMPORTS
from core.handlers.privatechat_functions.send_welcome import send_welcome
from core.handlers.privatechat_functions.show_user import show_user, show_user_deeplink
from core.handlers.privatechat_functions.status import status
from core.handlers.privatechat_functions.unmute import unmute
from core.utils.delete_old_ids import setup_schedule
from core.utils.is_chat_admin import get_admins_ids
from core.filters.admin_filter import AdminFilter
from core.middlewares.admins_mw import AdminMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
admins = []

# webhook control
async def on_startup():
    await async_main()
    await setup_schedule()
    print('startup', admins)
    await bot.send_message(-1001868029361, 'бот запущен')


# stopping app
async def on_shutdown():
    await bot.send_message(-1001868029361, 'бот остановлен')


# HANDLERS
async def start():
    admins = await get_admins_ids()
    print('start', admins)
    # CALLBACK HANDLERS
    dp.update.middleware.register(AdminMiddleware(admins=admins))
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.callback_query.register(show_user_react, F.data.startswith('show_user'))

    # debug
    dp.message.register(eraser, Command(commands='eraser'))

    # GROUP CHAT FUNCTION REGISTERS
    dp.message.register(mute, Command(commands='mute'), AdminFilter())
    dp.message.register(add_unblocks, Command(commands='add_unblocks'), AdminFilter())
    dp.message.register(join_cleaner, F.type.in_(Config.MESSAGES_FOR_DELETE))

    # PRIVATE HANDLERS
    dp.message.register(show_user_deeplink, F.chat.type == 'private', CommandStart(deep_link=True))
    dp.message.register(send_welcome, CommandStart(), F.type == 'private')
    dp.message.register(send_report, Command(commands=['send_report']), F.type == 'private')
    dp.message.register(status,  Command(commands=['status']), F.type == 'private')
    dp.message.register(bot_help, Command(commands=['help']), F.type == 'private')
    dp.message.register(unmute, Command(commands=['unmute']), F.type == 'private')
    dp.message.register(get_chat_id, Command(commands=['get_chat_id']), F.type == 'private')
    dp.message.register(show_user, Command(commands=['show_user']), F.type == 'private')
    dp.message.register(know_id)  # перехватываем все сообщения, вносим в базу

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start())
