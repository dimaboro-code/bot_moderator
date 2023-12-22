from aiogram import types, Bot
from aiogram.exceptions import TelegramAPIError
from typing import Set, List

from core.config import bot as my_bot
from core.config import Config


async def is_chat_admin(user_id: int):

    for chat_id in Config.CHATS:
        moderator: types.ChatMember = await my_bot.get_chat_member(
            chat_id=chat_id, user_id=user_id)
        moderators = await my_bot.get_chat_administrators(chat_id)
        if moderator in moderators:
            return True
        return False


async def get_admins_ids(bot: Bot = my_bot, chats: List[int] = Config.CHATS) -> List[int]:
    admins_set: Set[int] = set()
    try:
        for chat_id in chats:
            moderators: List[types.ChatMemberAdministrator] = await bot.get_chat_administrators(chat_id=chat_id)
            for moderator in moderators:
                admins_set.add(moderator.user.id)
    except Exception as e:
        # Обработка ошибок при вызове функции bot.get_chat_administrators()
        print(f"Ошибка при получении списка администраторов: {e}")
    return list(admins_set)

