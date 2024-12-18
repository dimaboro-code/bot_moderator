from typing import List

from aiogram import types, Bot

from core import ConfigVars
from core.database_functions.db_functions import add_mute
from core.models.data_models import UserData
from core.utils.restrict import restrict
from core.utils.send_report import send_bug_report, send_mute_report


async def mute(data: UserData, bot: Bot, silent: bool = False, chats: List[int] = ConfigVars.CHATS,
               permissions: types.ChatPermissions = ConfigVars.MUTE_SETTINGS):
    """
    Мьют с занесением данных в бд и отчетом.
    Args:
        silent: True, если нужно без отчета о мьюте
        data: данные о мьюте в формате UserData
        bot: бот
        chats: Список чатов, в которых мьютим
        permissions: Как именно мьютим, разрешения

    Returns: False если что-то не сработало, True если все ок

    """
    restriction = await restrict(user_id=data.user_id, chat_id_orig=data.chat_id, bot=bot,
                                 chats=chats, permissions=permissions)
    # если мьют не прошел
    if restriction is False:
        return False
    # Если мьют прошел - добавляем в базу. В будущем по этому значению можно мьютить старых замьюченых в новых чатах
    muted = await add_mute(data.for_mute)
    if not muted:
        problem = 'Мьют не добавлен в базу данных.'
        await send_bug_report(problem=problem, **data.as_dict(), bot=bot)
        return False
    # отправляем отчет в канал
    if not silent:
        try:
            await send_mute_report(**data.as_dict(), bot=bot)
        except Exception as e:
            problem = f'Мьют, не удалось отправить отчет. Ошибка: {e}'
            await send_bug_report(problem=problem, **data.as_dict(), bot=bot)
            return False
    # Мьют прошел (минимум в одном чате), инфа в базе, отчет в канале
    return True
