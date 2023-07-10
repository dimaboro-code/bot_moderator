from aiogram import types
from db import get_id, add_id


async def know_id(message: types.Message):
    username = message.from_user.username
    user_id = message.from_user.id

    try:
        if await get_id(username) is not None:
            return

        async with add_id(username=username, user_id=user_id):
            pass

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
