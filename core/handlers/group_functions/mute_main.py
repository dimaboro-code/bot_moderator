from aiogram import types, Bot
from typing import List

from core.config_vars import ConfigVars
from core.models.data_models import UserData
from core.utils.delete_message import delete_message
from core.utils.send_report import send_report_to_channel, send_report_to_group
from core.database_functions.db_functions import get_id, add_mute
from core.utils.is_username import is_username
from core.utils.restrict import restrict


async def mute_handler(moderator_message: types.Message, bot: Bot):
    permission = await checks(moderator_message, bot)
    if permission[0] is False:
        answer_message = await moderator_message.reply(permission[1])
        await delete_message(answer_message, 2)
        await delete_message(moderator_message)
        return

    if permission[0] is True:
        user_id = permission[1]

    else:
        print('Ошибка выполнения checks')
        return

    data = UserData()
    data.parse_message(moderator_message, user_id)

    success = await mute(data=data, bot=bot)
    if not success:
        msg = await moderator_message.answer('Мьют не прошел, отчет об ошибке отправлен разработчику')
        await delete_message(msg, 1)

    success_message = await moderator_message.answer(
        f'Пользователь {data.username} попал в мьют.'
    )
    try:
        await bot.delete_message(
            chat_id=moderator_message.chat.id,
            message_id=moderator_message.reply_to_message.message_id
        )
    except Exception as e:
        print('Сообщение с нарушением не удалено, ошибка:', e)

    await delete_message(moderator_message)
    await delete_message(success_message, 1)


async def mute(data: UserData, bot: Bot, chats: List[int] = ConfigVars.CHATS,
               permissions: types.ChatPermissions = ConfigVars.MUTE_SETTINGS):
    """
    Мьют с занесением данных в бд и отчетом.
    Args:
        data: данные о мьюте в формате UserData
        bot: бот
        chats: Список чатов, в которых мьютим
        permissions: Как именно мьютим, разрешения

    Returns: False если что-то не сработало, True если все ок

    """
    restriction = await restrict(user_id=data.user_id, chat_id=data.chat_id, bot=bot,
                                 chats=chats, permissions=permissions)

    # если мьют не прошел
    if restriction is False:
        return False

    # Если мьют прошел - добавляем в базу. В будущем по этому значению можно мьютить старых замьюченых в новых чатах
    muted = await add_mute(data.for_mute)
    if not muted:
        problem = 'Мьют не добавлен в базу данных.'
        await send_report_to_group(problem=problem, **data.as_dict())
        return False

    # отправляем отчет в канал
    try:
        await send_report_to_channel(**data.as_dict())
    except Exception as e:
        problem = f'Мьют, не удалось отправить отчет. Ошибка: {e}'
        await send_report_to_group(problem=problem, **data.as_dict())
        return False

    # Мьют прошел (минимум в одном чате), инфа в базе, отчет в канале
    return True  # TODO переделать в модель для данных


async def checks(moderator_message: types.Message, bot: Bot):
    # Есть два вида работы функции мьют
    # По юзернейму и по реплею
    # Если есть и то, и то, выбираем реплей.

    username = is_username(moderator_message.text)

    if username is not None:
        print(f'username{username}')

        user_id = await get_id(username)
        if user_id is None:
            return False, 'К сожалению, пользователя нет в базе.'

        print(f'user_id: {user_id}')

        if len(moderator_message.text.strip().split()) < 3:
            return False, 'Команда не содержит сообщение о причине мьюта'

        member = await bot.get_chat_member(moderator_message.chat.id, user_id)
        if member.status == 'restricted' and not member.can_send_messages:
            return False, 'Пользователь уже в мьюте'

        return True, user_id

    else:

        if not moderator_message.reply_to_message:
            return False, 'Команда должна быть ответом на сообщение или включать в себя юзернейм'

        user_id = moderator_message.reply_to_message.from_user.id

        if len(moderator_message.text.strip().split()) < 2:
            return False, 'Команда не содержит сообщение о причине мьюта'

        member = await bot.get_chat_member(moderator_message.chat.id, user_id)
        if member.status == 'restricted' and not member.can_send_messages:
            return False, 'Пользователь уже в мьюте'

        return True, user_id
