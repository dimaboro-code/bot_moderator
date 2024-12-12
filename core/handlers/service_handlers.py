from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.types import Message

from core import ConfigVars
from core.database_functions.db_functions import get_last_mute, add_lives
from core.filters.filters import CapchaChatFilter
from core.models.data_models import UserData
from core.services.join_cleaner import join_cleaner
from core.services.mute import mute

service_router = Router()
service_router.message.filter(F.content_type.in_(ConfigVars.MESSAGES_FOR_DELETE))


@service_router.message()
async def join_cleaner_handler(message: Message):
    await join_cleaner(message)
