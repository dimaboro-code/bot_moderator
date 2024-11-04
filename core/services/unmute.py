from typing import List

from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest

from core import ConfigVars
from core.database_functions.db_functions import get_user, get_last_mute, add_lives, db_unmute
from core.services.status import status
from core.utils.restrict import restrict
from core.utils.send_report import send_bug_report


async def unmute(user_id, bot: Bot, chats: List[int] = ConfigVars.CHATS,
                 permissions: types.ChatPermissions = ConfigVars.UNMUTE_SETTINGS):
    user_data = await get_user(user_id)
    user_last_mute = await get_last_mute(user_id)
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
    except TelegramBadRequest as e:
        problem = f'Анмьют, нет доступа к чату последнего мьюта, ошибка: {e}'
        await send_bug_report(user_id=user_id, chat_id='None', user_username=user_id,
                              chat_username='None', problem=problem, bot=bot)
        answer = 'Нет доступа к чату последнего мьюта'
        return False, answer
    answer = None
    match member:
        case types.ChatMemberMember():
            answer = ('Вы уже разблокированы. Если у вас сохраняется блокировка,'
                      ' обратитесь к модераторам, например, @deanrie.')
        case types.ChatMemberAdministrator() | types.ChatMemberOwner():
            answer = 'Вы админ. Вас нельзя заблокировать.'
        case types.ChatMemberRestricted(can_send_messages=True):
            await add_lives(user_id=user_id)
        case types.ChatMemberBanned():
            answer = 'Вы забанены. Для снятия блокировки можете обратиться к админам.'
        case types.ChatMemberLeft():
            answer = 'Вы разблокированы в чате, в котором были заблокированы. Можете вновь вступить в него'
    if answer:
        return False, answer
    restriction = await restrict(user_id=user_id, chat_id_orig=user_id, bot=bot, chats=chats, permissions=permissions)
    # если разблок не прошел
    if restriction is False:
        answer = 'Не удалось разблокировать, отчет направлен разработчику. Обратитесь к модераторам, например, @deanrie'
        return False, answer
    unmuted = await db_unmute(user_id)
    if unmuted is False:
        answer = 'Вы разблокированы. Не удалось обновить данные в базе, отчет направлен разработчику.'
        return False, answer
    answer = await status(user_id, bot)
    return True, answer


async def admin_unmute(user_id, bot: Bot, chats: List[int] = ConfigVars.CHATS,
                       permissions: types.ChatPermissions = ConfigVars.UNMUTE_SETTINGS):
    user_last_mute = await get_last_mute(user_id)
    if user_last_mute is None:
        answer = 'Ошибка базы данных, пользователь не найден. Сообщить о баге @dimaboro'
        return False, answer

    restriction = await restrict(user_id=user_id, chat_id_orig=user_id, bot=bot, chats=chats, permissions=permissions)
    # если разблок не прошел
    if restriction is False:
        answer = 'Не удалось разблокировать, отчет направлен разработчику. Обратитесь к модераторам, например, @deanrie'
        return False, answer

    unmuted = await db_unmute(user_id)
    if unmuted is False:
        answer = 'Вы разблокированы. Не удалось обновить данные в базе, отчет направлен разработчику.'
        return False, answer

    answer = await status(user_id, bot)
    return True, answer
