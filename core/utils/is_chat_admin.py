from aiogram import types

from core.config import bot
from core.config import CHATS


async def is_chat_admin(user_id):

    for chat_id in CHATS:
        moderator: types.ChatMember = await bot.get_chat_member(
            chat_id=chat_id, user_id=user_id)
        moderators = await bot.get_chat_administrators(chat_id)
        if moderator in moderators:
            return True
        return False
