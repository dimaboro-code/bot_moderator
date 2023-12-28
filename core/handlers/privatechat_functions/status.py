from aiogram import types

from core.config import bot
from core.database_functions.db_functions import *


async def status(message: types.Message):
    """
     start func
    :param message:
    :return:
    """
    user_id = message.from_user.id

    last_mute = await get_last_mute(user_id)

    if last_mute is None:
        await message.answer('Вы ранее не блокировались ботом')
        return

    chat = await bot.get_chat(last_mute["chat_id"])
    user_data = await get_user(user_id)
    answer = (f'Статус: {("без ограничений", "в мьюте")[user_data["is_muted"]]}\n'
              f'Осталось разблоков: {user_data["user_blocks"]}\n\n'
              f'Последний мьют\n'
              f'Причина: {last_mute["moderator_message"]}\n'
              f'Чат: @{chat.username}\n'
              f'Админ: @{last_mute["admin_username"]}\n'
              # f'Сообщение: {reason_to_mute.text}\n'
              f'Дата мьюта: {last_mute["date_of_mute"]}')
    await message.answer(answer)
