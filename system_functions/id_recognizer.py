from aiogram import types
from db import get_id, add_id, check_know_id


async def know_id(message: types.Message):
    username = message.from_user.username
    user_id = message.from_user.id

    if username is None:
        print('Нет юзернейма в сообщении, id', user_id)
        print(message)
        return

    if await get_id(username) is not None:
        print('id найден, юзернейм ', username)
        return

    for i in range(1, 6):
        await add_id(username=username, user_id=user_id)
        check_username = await check_know_id(user_id)
        if check_username is None:
            print(f'Нет юзернейма в базе данных, попытка {i}')
            continue
        break
