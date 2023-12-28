import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from core.database_functions.db_functions import add_id, add_user


async def know_id(message: types.Message, session: AsyncSession):
    username = message.from_user.username
    user_id = message.from_user.id

    user = await add_user(user_id=user_id, session=session)
    if not user:
        return False

    un_id = await add_id(username=username, user_id=user_id, session=session)
    if not un_id:
        return False

    logging.info(f'Пользователь @{username} c ID {user_id} добавлен в базу')
    return True
