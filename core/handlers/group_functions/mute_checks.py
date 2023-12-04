from aiogram import types
from core.utils.is_username import is_username
from config import bot
from core.db import get_id


async def checks(moderator_message: types.Message):
    # Есть два вида работы функции мьют
    # По юзернейму и по реплею
    # Если есть и то, и то, выбираем реплей.

    username = await is_username(moderator_message.text)

    if username is not None:
        print(f'username{username}')

        user_id = await get_id(username)
        if user_id is None:

            return False, 'К сожалению, пользователя нет в базе.'

        print(f'user_id: {user_id}')

        if len(moderator_message.text.strip().split()) < 3:
            return False, 'Команда не содержит сообщение о причине мьюта'

        member = await bot.get_chat_member(moderator_message.chat.id, user_id)
        print('Статус:', member.status, '\n')
        if member.status == 'restricted' and not member.can_send_messages:
            return False, 'Пользователь уже в мьюте'

        return True, user_id

    else:
        print('No username')

        if not moderator_message.reply_to_message:
            print('Command has no user to mute')
            return False, 'Команда должна быть ответом на сообщение или включать в себя юзернейм'

        user_id = moderator_message.reply_to_message.from_user.id

        if len(moderator_message.text.strip().split()) < 2:
            return False, 'Команда не содержит сообщение о причине мьюта'

        member = await bot.get_chat_member(moderator_message.chat.id, user_id)
        print('Статус:', member.status, '\n',)
        if member.status == 'restricted' and not member.can_send_messages:

            return False, 'Пользователь уже в мьюте'

        return True, user_id
