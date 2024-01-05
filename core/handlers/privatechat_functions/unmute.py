from typing import List
from aiogram import types, Bot
from aiogram.exceptions import TelegramBadRequest

from core.config_vars import ConfigVars
from core.database_functions.db_functions import get_user, get_last_mute, db_unmute, add_lives
from core.handlers.privatechat_functions.status import status
from core.utils.restrict import restrict
from core.utils.send_report import send_report_to_group


async def unmute_handler(message: types.Message, bot: Bot, session):
    user_id = message.from_user.id
    success, answer = await unmute(user_id=user_id, bot=bot, session=session)
    if success:
        await message.answer('Успешно')
        await message.answer(answer)
    else:
        await message.answer(answer)


async def unmute(user_id, bot: Bot, session, chats: List[int] = ConfigVars.CHATS,
                 permissions: types.ChatPermissions = ConfigVars.UNMUTE_SETTINGS):
    user_data = await get_user(user_id, session)
    user_last_mute = await get_last_mute(user_id, session)
    if user_last_mute is None:
        answer = ('Вас нет в моей базе. Если у вас сохраняется блокировка,'
                  ' обратитесь к модераторам, например, @deanrie.')
        return False, answer

    if user_data['user_blocks'] <= 0:
        answer = ('К сожалению, у вас закончились разблоки. Теперь вы можете '
                  'остаться в чатах в режиме читателя.')
        return False, answer

    try:
        member = await bot.get_chat_member(user_last_mute['chat_id'], user_id)
        if isinstance(member, types.ChatMemberMember):
            answer = ('Вы уже разблокированы. Если у вас сохраняется блокировка,'
                      ' обратитесь к модераторам, например, @deanrie.')
            return False, answer
        if member in (types.ChatMemberAdministrator, types.ChatMemberOwner):
            answer = 'Вы админ. Вас нельзя заблокировать.'
            return False, answer
        if isinstance(member, types.ChatMemberRestricted) and member.can_send_messages is True:
            await add_lives(user_id=user_id, session=session)
    except TelegramBadRequest as e:
        problem = f'Анмьют, нет доступа к чату последнего мьюта, ошибка: {e}'
        await send_report_to_group(user_id, 'None', user_id, 'None', problem)
        answer = 'Нет доступа к чату последнего мьюта'
        return False, answer

    restriction = await restrict(user_id=user_id, chat_id=user_id, bot=bot, chats=chats, permissions=permissions)
    # если разблок не прошел
    if restriction is False:
        answer = 'Не удалось разблокировать, отчет направлен разработчику. Обратитесь к модераторам, например, @deanrie'
        return False, answer

    unmuted = await db_unmute(user_id, session)
    if unmuted is False:
        answer = 'Вы разблокированы. Не удалось обновить данные в базе, отчет направлен разработчику.'
        return False, answer

    answer = await status(user_id, session)
    return True, answer
