from typing import Set, List

from aiogram import types, Bot

from core.config import ConfigVars


async def get_admins_ids(bot: Bot, chats: List[int] = ConfigVars.CHATS) -> List[int]:
    admins_set: Set[int] = set()
    for chat_id in chats:
        try:
            moderators: List[types.ChatMemberAdministrator] = await bot.get_chat_administrators(chat_id=chat_id)
            for moderator in moderators:
                admins_set.add(moderator.user.id)
        except Exception as e:
            # Обработка ошибок при вызове функции bot.get_chat_administrators()
            print(f"Ошибка при получении списка администраторов: {e}")
    return list(admins_set)
