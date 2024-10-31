# all actions logger, currently doesn't exist
import logging

# run webhook
from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# settings import
from core.config_vars import ConfigVars
# full database import
from core.database_functions.db_functions import create_db, db_get_strict_chats
from core.handlers import all_routers
# GROUP FUNCTION IMPORTS
from core.middlewares.config_mw import ConfigMiddleware
# SETUP FUNCTIONS
from core.services.db_old_ids_cleaner import setup_schedule
from core.utils.is_chat_admin import get_admins_ids
from core.config import bot, dp

# Configure logging
logging.basicConfig(level=logging.INFO)


# webhook control
async def on_startup(bot: Bot):
    await create_db()
    await setup_schedule()
    admins = await get_admins_ids()
    dp['admins'] = admins
    dp['strict_chats'] = await db_get_strict_chats()
    dp['reason_message'] = dict()
    await bot.set_webhook(url=ConfigVars.WEBHOOK_URL,
                          drop_pending_updates=True,
                          secret_token=ConfigVars.WEBHOOK_SECRET)


def start_app():
    dp.update.middleware.register(ConfigMiddleware())
    for router in all_routers:
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
    start_app()
