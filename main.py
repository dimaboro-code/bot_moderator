# all actions logger, currently doesn't exist
import logging

# run webhook
from aiogram.utils.executor import start_webhook

# settings import
from config import bot, dp, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, MESSAGES_FOR_DELETE

# full database import
from db import *

# GROUP FUNCTION IMPORTS
from group_functions.mute_new.mute_main import mute
from group_functions.join_cleaner import join_cleaner
from group_functions.add_unblocks import add_unblocks

# SYSTEM FUNCTION IMPORTS
from system_functions.eraser import eraser
from system_functions.get_chat_id import get_chat_id
from system_functions.id_recognizer import know_id
from system_functions.delete_old_ids import setup_schedule


# PRIVATECHAT FUCNTION IMPORTS
from privatechat_functions.send_welcome import send_welcome
from privatechat_functions.unmute import unmute
from privatechat_functions.status import status
from privatechat_functions.bot_help import bot_help

# Configure logging
logging.basicConfig(level=logging.INFO)


# webhook control
async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await database.connect()
    await create_table_ids()  # можно удалить в следующем обновлении. Нужно, чтобы разово создать таблицу
    await setup_schedule()


# stopping app
async def on_shutdown(dispatcher):
    await database.disconnect()
    await bot.delete_webhook()

# HANDLERS

# debug
dp.register_message_handler(eraser, commands=['eraser'], commands_prefix='!/')

# GROUP CHAT FUNCTION REGISTERS
dp.register_message_handler(mute, commands=['mute'], is_chat_admin=True, commands_prefix='!/')
dp.register_message_handler(add_unblocks, commands=['add_unblocks'], is_chat_admin=True, commands_prefix='!/')
dp.register_message_handler(join_cleaner, content_types=MESSAGES_FOR_DELETE)

# PRIVATE HANDLERS
dp.register_message_handler(send_welcome, commands_prefix='!/', commands=['start'], chat_type='private')
dp.register_message_handler(status, commands_prefix='!/', commands=['status'], chat_type='private')
dp.register_message_handler(bot_help, commands_prefix='!/', commands=['help'], chat_type='private')
dp.register_message_handler(unmute, commands_prefix='!/', commands=['unmute'], chat_type='private')
dp.register_message_handler(get_chat_id, commands_prefix='!/', commands=['get_chat_id'], chat_type='private')
dp.register_message_handler(know_id)  # перехватываем все сообщения, вносим в базу


if __name__ == '__main__':

    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
