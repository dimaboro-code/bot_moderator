# all actions logger, currently doesn't exist
import asyncio
import logging

# run webhook
from aiogram import F, Router
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
from core.utils.delete_message import delete_message
from core.filters.admin_filter import AdminFilter
from core.middlewares.admins_mw import AdminMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)


# webhook control
async def on_startup():
    await async_main()
    await setup_schedule()
    msg = await bot.send_message(-1001868029361, 'бот запущен')
    await delete_message(msg, 2)


# stopping app
async def on_shutdown():
    msg = await bot.send_message(-1001868029361, 'бот остановлен')
    await delete_message(msg, 2)


# HANDLERS
async def setup_handlers(router: Router):
    router.startup.register(on_startup)
    router.shutdown.register(on_shutdown)
    router.callback_query.register(show_user_react, F.data.startswith('show_user'))

    # debug
    router.message.register(eraser, Command(commands='eraser'))

    # GROUP CHAT FUNCTION REGISTERS
    router.message.register(mute, Command(commands='mute'), AdminFilter())
    router.message.register(add_unblocks, Command(commands='add_unblocks'), AdminFilter())
    router.message.register(join_cleaner, F.content_type.in_(Config.MESSAGES_FOR_DELETE))

    # PRIVATE HANDLERS
    router.message.register(show_user_deeplink, F.chat.type == 'private', CommandStart(deep_link=True))
    router.message.register(send_welcome, CommandStart(), F.chat.type == 'private')
    router.message.register(send_report, Command(commands='send_report'), F.chat.type == 'private')
    router.message.register(status, Command(commands='status'), F.chat.type == 'private')
    router.message.register(bot_help, Command(commands='help'), F.chat.type == 'private')
    router.message.register(unmute, Command(commands='unmute'), F.chat.type == 'private')
    router.message.register(get_chat_id, Command(commands='get_chat_id'), F.chat.type == 'private')
    router.message.register(show_user, Command(commands='show_user'), F.chat.type == 'private')
    router.message.register(know_id)  # перехватываем все сообщения, вносим в базу
    return router


async def start():
    admins = await get_admins_ids()
    router = await setup_handlers(router=Router())
    dp.include_router(router)
    dp.update.middleware.register(AdminMiddleware(admins=admins))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start())
