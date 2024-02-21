from aiogram import types, Bot

from core.database_functions.db_functions import get_user, get_last_mute, get_username, get_all_mutes
from core.utils.send_report import send_bug_report


async def status(user_id: int, session, bot: Bot):
    user_data = await get_user(user_id=user_id, session=session)
    if user_data is None:
        answer = 'Пользователя нет в базе данных'
        return answer

    user_last_mute = await get_last_mute(user_id=user_id, session=session)
    username = await get_username(user_id=user_id, session=session)
    if user_last_mute is None:
        answer = (f'Пользователь: @{username}\n'
                  f'user id: {user_id},\n'
                  'Статус: без ограничений\n'
                  f'Осталось разблоков: {user_data["user_blocks"]}\n'
                  'Пользователь ранее не блокировался')
        return answer
    try:
        chat: types.Chat = await bot.get_chat(user_last_mute["chat_id"])
        chat_username: str | None = chat.username
    except Exception as e:
        chat_username = None
        await send_bug_report(user_id=user_id, user_username=username, chat_id='private', chat_username='None',
                              problem=f'Статус, не удалось получить данные о чате, ошибка: {e}')
    answer = (f'Пользователь: @{username}\n'
              f'user id: {user_id},\n'
              f'Статус: {("без ограничений", "в мьюте")[user_data["is_muted"]]}\n'  #
              f'Осталось разблоков: {user_data["user_blocks"]}\n\n'
              f'Последний мьют\n'
              f'Причина: {user_last_mute["moderator_message"]}\n'
              f'Чат: @{chat_username}\n'
              f'Админ: @{user_last_mute["admin_username"]}\n'
              f'Дата мьюта: {user_last_mute["date_of_mute"]}')
    return answer


async def status_log(user_id: int, session, bot: Bot):
    user_data = await get_user(user_id=user_id, session=session)
    if user_data is None:
        answer = 'Пользователя нет в базе данных'
        return answer

    user_mutes = await get_all_mutes(user_id=user_id, session=session)
    username = await get_username(user_id=user_id, session=session)
    if user_mutes is None:
        answer = 'Пользователь ранее не блокировался'
        return answer

    answer_list = []
    for mute in user_mutes:
        try:
            chat: types.Chat = await bot.get_chat(mute["chat_id"])
            chat_username: str | None = chat.username
        except Exception as e:
            chat_username = None
            await send_bug_report(user_id=user_id, user_username=username, chat_id='private', chat_username='None',
                                  problem=f'Статус, не удалось получить данные о чате, ошибка: {e}')
        answer_list.append(f'Мьют №{mute["id"]}\n'
                           f'Причина: {mute["moderator_message"]}\n'
                           f'Чат: @{chat_username}\n'
                           f'Админ: @{mute["admin_username"]}\n'
                           f'Дата мьюта: {mute["date_of_mute"]}')
    answer = '\n\n'.join(answer_list)
    return answer
