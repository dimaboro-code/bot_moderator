# all actions logger, currently doesn't exist
import logging

# run webhook
from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# settings import
from core.config import bot, dp, Config
# full database import
from core.database_functions.db_functions import async_main
from core.filters.admin_filter import AdminFilter
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

# Configure logging
logging.basicConfig(level=logging.INFO)


# webhook control
async def on_startup(bot: Bot):
    await async_main()
    await setup_schedule()
    admins = await get_admins_ids()
    dp['admins'] = admins
    await bot.set_webhook(url=Config.WEBHOOK_URL, drop_pending_updates=True, secret_token=Config.WEBHOOK_SECRET)


# HANDLERS
def setup_handlers(router: Router):
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


def start():
    router = setup_handlers(router=Router())
    dp.include_router(router)
    dp.startup.register(on_startup)
    # dp.update.middleware.register(AdminMiddleware(admins=admins))

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=Config.WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=Config.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=Config.WEBAPP_HOST, port=Config.WEBAPP_PORT)


if __name__ == '__main__':
    start()
