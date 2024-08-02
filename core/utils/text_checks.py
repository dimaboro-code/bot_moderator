from aiogram import Bot
from aiogram.types import Message

from core.database_functions.db_functions import get_id
from core.utils.get_username_from_text import is_username


async def checks(moderator_message: Message, bot: Bot):
    # Есть два вида работы функции мьют
    # По юзернейму и по реплею
    # Если есть и то, и то, выбираем реплей.

    username = is_username(moderator_message.text)

    if username is not None:
        user_id = await get_id(username)
        if user_id is None:
            return False, 'К сожалению, пользователя нет в базе.'

        if len(moderator_message.text.strip().split()) < 3:
            return False, 'Команда не содержит сообщение о причине мьюта'

        member = await bot.get_chat_member(moderator_message.chat.id, user_id)
        if member.status == 'restricted' and not member.can_send_messages:
            return False, 'Пользователь уже в мьюте'

        return True, user_id

    if not moderator_message.reply_to_message:
        return False, 'Команда должна быть ответом на сообщение или включать в себя юзернейм'

    user_id = moderator_message.reply_to_message.from_user.id

    if len(moderator_message.text.strip().split()) < 2:
        return False, 'Команда не содержит сообщение о причине мьюта'

    member = await bot.get_chat_member(moderator_message.chat.id, user_id)
    if member.status == 'restricted' and not member.can_send_messages:
        return False, 'Пользователь уже в мьюте'

    return True, user_id


async def get_id_from_text(text: str) -> int:
    pure_text: str = text.split()[1]

    if pure_text.isdigit():
        user_id = int(pure_text)
    else:
        username = is_username(pure_text)
        if username is not None:
            pure_text = username
        user_id = await get_id(f'{pure_text}')
    return user_id
