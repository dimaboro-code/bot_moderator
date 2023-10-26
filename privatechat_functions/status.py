from aiogram import types

from config import bot

from db import *


async def status(message: types.Message):
    ''' start func
    :param message:
    :return:
    '''
    user_id = message.from_user.id

    is_in_database = await in_database(user_id=user_id)

    if not is_in_database:
        await message.answer('Статус: У вас осталось 3 разблока.')
        return None

    last_mute = await get_last_mute(user_id)

    if last_mute is None:
        await message.answer('Нет данных о мьюте')
        return
    else:
        chat = await bot.get_chat(last_mute["chat_id"])

    user_data = await get_user(user_id)

    answer = (f'Статус: {("без ограничений", "в мьюте")[user_data["is_muted"]]}\n' 
              f'Осталось разблоков: {user_data["user_blocks"]}\n\n' 
              f'Последний мьют\n'
              f'Причина: {last_mute["moderator_message"]}\n' 
              f'Чат: {chat.username}\n' 
              f'Админ: {last_mute["admin_username"]}\n' 
              # f'Сообщение: {reason_to_mute.text}\n'
              f'Дата мьюта: {last_mute["date_of_mute"]}')
    # await delete_message(reason_to_mute)
    await message.answer(answer)