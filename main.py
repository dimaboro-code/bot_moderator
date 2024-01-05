# all actions logger, currently doesn't exist
import logging

# run webhook
from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# settings import
from core.config_vars import ConfigVars
# full database import
from core.database_functions.db_functions import async_main
from core.filters.admin_filter import AdminFilter
from core.handlers.callback_privatechat_functions.callback_show_users import show_user_react
# GROUP FUNCTION IMPORTS
from core.handlers.group_functions.add_unblocks import add_unblocks
from core.handlers.group_functions.join_cleaner import join_cleaner
from core.handlers.group_functions.mute_main import mute_handler
# PRIVATECHAT FUNCTION IMPORTS
from core.handlers.privatechat_functions.bot_help import bot_help
from core.handlers.privatechat_functions.eraser import eraser
from core.handlers.privatechat_functions.get_chat_id import get_chat_id
from core.handlers.privatechat_functions.send_report import send_report_handler
from core.handlers.privatechat_functions.send_welcome import send_welcome
from core.handlers.privatechat_functions.show_user import show_user_handler
from core.handlers.privatechat_functions.status import status
from core.handlers.privatechat_functions.test_db_handler import test_db_handler
from core.handlers.privatechat_functions.unmute import unmute
from core.middlewares.add_user_mw import AddUserMiddleware
from core.middlewares.config_mw import ConfigMiddleware
# SETUP FUNCTIONS
from core.utils.delete_old_ids import setup_schedule
from core.utils.is_chat_admin import get_admins_ids
from core.config import bot, dp, async_session

# Configure logging
logging.basicConfig(level=logging.INFO)


# webhook control
async def on_startup(bot: Bot):
    await async_main()
    await setup_schedule()
    admins = await get_admins_ids()
    dp['admins'] = admins
    await bot.set_webhook(url=ConfigVars.WEBHOOK_URL,
                          drop_pending_updates=True,
                          secret_token=ConfigVars.WEBHOOK_SECRET)


# HANDLERS
def setup_handlers(router: Router):
    router.callback_query.register(show_user_react, F.data.startswith('show_user'))

    router.message.middleware.register(AddUserMiddleware())  # перехватываем все сообщения, вносим в базу
    # debug
    router.message.register(eraser, Command(commands='eraser'))

    # GROUP CHAT FUNCTION REGISTERS
    router.message.register(mute_handler, Command(commands='mute'), AdminFilter())
    router.message.register(add_unblocks, Command(commands='add_unblocks'), AdminFilter())
    router.message.register(join_cleaner, F.content_type.in_(ConfigVars.MESSAGES_FOR_DELETE))

    # PRIVATE HANDLERS
    router.message.register(test_db_handler, F.chat.type == 'private', AdminFilter(),
                            Command('test_db'))
    router.message.register(show_user_handler, F.chat.type == 'private', AdminFilter(),
                            CommandStart(deep_link=True))
    router.message.register(send_welcome, CommandStart(), F.chat.type == 'private')
    router.message.register(send_report_handler, AdminFilter(),
                            Command(commands='send_report'), F.chat.type == 'private')
    router.message.register(status, Command(commands='status'), F.chat.type == 'private')
    router.message.register(bot_help, Command(commands='help'), F.chat.type == 'private')
    router.message.register(unmute, Command(commands='unmute'), F.chat.type == 'private')
    router.message.register(get_chat_id, Command(commands='get_chat_id'), F.chat.type == 'private')
    router.message.register(show_user_handler, Command(commands='show_user'), F.chat.type == 'private', AdminFilter())
    return router


def start():
    router = setup_handlers(router=Router())
    dp.update.middleware.register(ConfigMiddleware(async_session))
    dp.include_router(router)
    dp.startup.register(on_startup)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=ConfigVars.WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=ConfigVars.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=ConfigVars.WEBAPP_HOST, port=ConfigVars.WEBAPP_PORT)


if __name__ == '__main__':
    start()
