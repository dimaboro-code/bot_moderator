from aiogram import types

from core.database_functions.db_functions import check_known_id, add_or_update_id, in_database, add_user


async def know_id(message: types.Message):
    username = message.from_user.username
    user_id = message.from_user.id

    if not await in_database(user_id):
        await add_user(user_id)

    if username is None:
        print('Нет юзернейма в сообщении, id', user_id)
        print(message)
        return


    check_username = await check_known_id(user_id)
    print(check_username)
    if check_username is None:
        await add_or_update_id(username=username, user_id=user_id)
        # print('Не удалось добавить в базу юзернейм.')

