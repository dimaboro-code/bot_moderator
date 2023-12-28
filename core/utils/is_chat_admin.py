import logging
from typing import Set, List

from aiogram import types, Bot

from core.config_vars import ConfigVars
from core.config import bot as my_bot


async def is_chat_admin(user_id: int):
    for chat_id in ConfigVars.CHATS:
        moderator: types.ChatMember = await my_bot.get_chat_member(
            chat_id=chat_id, user_id=user_id)
        moderators = await my_bot.get_chat_administrators(chat_id)
        if moderator in moderators:
            logging.info('Легаси функция is_chat_admin')
            return True
        return False


async def get_admins_ids(bot: Bot = my_bot, chats: List[int] = ConfigVars.CHATS) -> List[int]:
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
