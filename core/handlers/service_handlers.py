from aiogram import Router, F
from aiogram.types import Message

from core import ConfigVars
from core.services.join_cleaner import join_cleaner

service_router = Router()
service_router.message.filter(F.content_type.in_(ConfigVars.MESSAGES_FOR_DELETE))


@service_router.message()
async def join_cleaner_handler(message: Message):
    await join_cleaner(message)
