import logging
from aiogram import types, Bot

from core.database_functions.db_functions import add_id, add_user
from core.utils.send_report import send_bug_report


async def add_user_to_db(message: types.Message, bot: Bot):
    username = message.from_user.username if isinstance(message.from_user.username, str) else 'None'
    user_id = message.from_user.id

    user = await add_user(user_id=user_id)
    un_id = await add_id(username=username, user_id=user_id)
    if not user or not un_id:
        user_id = user_id
        username = username
        chat_id = message.chat.id
        chat_username = message.chat.username
        problem = f'Не удалось добавить в базу: user={user}, un_id={un_id}'
        await send_bug_report(user_id=user_id, chat_id=chat_id, problem=problem, user_username=username,
                              chat_username=chat_username, bot=bot)
        return False

    logging.info(f'Пользователь @{username} c ID {user_id} добавлен в базу')
    return True
