# all actions logger, currently doesn't exist
import logging

# run webhook
from aiogram import filters
from aiogram.utils.executor import start_polling

# settings import
from core.config import bot, dp, MESSAGES_FOR_DELETE

# full database import
from core.database_functions.db_functions import async_main

# GROUP FUNCTION IMPORTS
from core.handlers.group_functions.mute_main import mute
from core.handlers.group_functions.join_cleaner import join_cleaner
from core.handlers.group_functions.add_unblocks import add_unblocks

# SYSTEM FUNCTION IMPORTS
from core.handlers.privatechat_functions.eraser import eraser
from core.handlers.privatechat_functions.get_chat_id import get_chat_id
from core.handlers.group_functions.id_recognizer import know_id
from core.utils.delete_old_ids import setup_schedule
from core.handlers.callback_privatechat_functions.callback_show_users import show_user_react
from core.handlers.privatechat_functions.send_report import send_report


# PRIVATECHAT FUCNTION IMPORTS
from core.handlers.privatechat_functions.send_welcome import send_welcome
from core.handlers.privatechat_functions.unmute import unmute
from core.handlers.privatechat_functions.status import status
from core.handlers.privatechat_functions.bot_help import bot_help
from core.handlers.privatechat_functions.show_user import show_user, show_user_deeplink


# Configure logging
logging.basicConfig(level=logging.INFO)


# webhook control
async def on_startup(dispatcher):
    await async_main()
    await setup_schedule()
    await bot.send_message(-1001868029361, 'бот запущен')


# stopping app
async def on_shutdown(dispatcher):
    await bot.send_message(-1001868029361, 'бот остановлен')


# HANDLERS

dp.register_callback_query_handler(show_user_react, filters.Text(startswith='show_user'))


# debug
dp.register_message_handler(eraser, commands=['eraser'], commands_prefix='!/')


# GROUP CHAT FUNCTION REGISTERS
dp.register_message_handler(mute, commands=['mute'], is_chat_admin=True, commands_prefix='!/')
dp.register_message_handler(add_unblocks, commands=['add_unblocks'], is_chat_admin=True, commands_prefix='!/')
dp.register_message_handler(join_cleaner, content_types=MESSAGES_FOR_DELETE)


# PRIVATE HANDLERS
dp.register_message_handler(show_user_deeplink, filters.CommandStart, filters.Text(contains=' '), chat_type='private')
dp.register_message_handler(send_welcome, commands_prefix='!/', commands=['start'], chat_type='private')
dp.register_message_handler(send_report, commands=['send_report'], chat_type='private')
dp.register_message_handler(status, commands_prefix='!/', commands=['status'], chat_type='private')
dp.register_message_handler(bot_help, commands_prefix='!/', commands=['help'], chat_type='private')
dp.register_message_handler(unmute, commands_prefix='!/', commands=['unmute'], chat_type='private')
dp.register_message_handler(get_chat_id, commands_prefix='!/', commands=['get_chat_id'], chat_type='private')
dp.register_message_handler(show_user, commands_prefix='!/', commands=['show_user'], chat_type='private')
dp.register_message_handler(know_id)  # перехватываем все сообщения, вносим в базу


if __name__ == '__main__':

    start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
