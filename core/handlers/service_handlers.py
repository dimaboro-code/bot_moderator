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


@service_router.message(CapchaChatFilter(), F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def capcha_handler(message: Message, bot: Bot, admins: list):
    await message.delete()
    user_id = message.from_user.id
    if user_id in admins:
        return
    # last_mute = await get_last_mute(user_id)
    # if last_mute:
    #     print('old user joined chat')
    #     # не новый пользователь
    #     return
    data = UserData()
    data.user_id = user_id
    data.username = str(message.from_user.username)
    data.admin_id = 114099198
    data.admin_username = 'dimaboro'
    data.chat_id = message.chat.id
    data.chat_username = message.chat.username
    data.reason_message = 'capcha'
    data.admin_username = 'dimaboro'
    data.is_reply = False
    await add_lives(user_id)
    await mute(data=data, bot=bot)


@service_router.message()
async def join_cleaner_handler(message: Message):
    await join_cleaner(message)
