from aiogram import types, Bot

from core.config_vars import ConfigVars
from core.models.data_models import UserData
from core.utils.delete_message import delete_message
from core.utils.restrict import restrict
from core.utils.send_report import send_report_to_channel, send_report_to_group
from core.database_functions.db_functions import get_id, add_mute
from core.utils.is_username import is_username


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
        print('Ошибка проверки мьюта')
        return

    data = UserData()
    data.parse_message(moderator_message, user_id)
    print(data.as_dict())

    success = await mute(data=data, bot=bot)
    if not success:
        msg = await moderator_message.answer('мьют не прошел, отчет направлен разработчику')
        await delete_message(msg, 1)
    success_message = await moderator_message.answer(
        f'Пользователь {data.username} попал в мьют.'
    )

    try:
        await bot.delete_message(
            chat_id=moderator_message.chat.id,
            message_id=moderator_message.reply_to_message.message_id
        )
        print('Сообщение с нарушением удалено')
    except Exception as e:
        print('Сообщение с нарушением не удалено, ошибка:', e)

    await delete_message(moderator_message)
    await delete_message(success_message, 1)


async def mute(data: UserData, bot: Bot, config_vars: ConfigVars = ConfigVars):
    chats = config_vars.CHATS
    for chat_id in chats:
        try:
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=data.user_id,
                permissions=config_vars.MUTE_SETTINGS,
                # mute time, if < 30 = forever
                until_date=10
            )
        except Exception as e:
            print(chat_id, ': ошибка:', e)

            problem = f'Не прошел мьют, ошибка: {e}'
            await send_report_to_group(problem=problem, **data.as_dict())
            continue

    # проверка мьюта в текущем чате
    member_actual_state = await bot.get_chat_member(chat_id=data.chat_id, user_id=data.user_id)
    if member_actual_state.status != 'restricted' or member_actual_state.can_send_messages:
        ans = await bot.send_message(chat_id=data.chat_id,
                                     text='Мьют не прошел, отчет об ошибке отправлен разработчику')
        await delete_message(ans, 1)
        return False

    print('Причина мьюта:', data.reason_message)

    await add_mute(data.for_mute)

    try:
        await send_report_to_channel(**data.as_dict())
    except Exception as problem:
        await send_report_to_group(problem=problem, **data.as_dict())
    return True


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
        print('Статус:', member.status)
        if member.status == 'restricted' and not member.can_send_messages:
            return False, 'Пользователь уже в мьюте'

        return True, user_id
