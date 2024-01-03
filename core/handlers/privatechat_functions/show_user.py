from typing import List

from aiogram import types

from core.config import bot
from core.database_functions.db_functions import get_id
from core.database_functions.db_functions import get_user, get_last_mute
from core.keyboards.show_user_keyboard import show_user_keyboard
from core.utils.is_username import is_username


async def show_user(message: types.Message, admins: List[int], dl: str = None):
    admin_id = message.from_user.id
    if admin_id not in admins:
        await message.answer('Вы не являетесь модератором сообщества')
        return

    username = is_username(message.text if not dl else dl)
    if username is None:
        await message.answer('Не указан username')
        return

    user_id = await get_id(username)
    if user_id is None:
        await message.answer('Пользователя нет в базе данных айди')
        return

    user_status = await get_user(user_id)
    if user_status is None:
        await message.answer('Пользователя нет в базе данных мьютов')
        return

    user_last_mute = await get_last_mute(user_id)
    if user_last_mute is None:
        await message.answer(f'Пользователь: @{username}\n'
                             f'Статус: без ограничений\n'
                             f'Осталось разблоков: 3\n'
                             f'Пользователь ранее не блокировался')
        return

    chat = await bot.get_chat(user_last_mute["chat_id"])
    answer = (f'Пользователь: @{username}\n'
              f'Статус: {("без ограничений", "в мьюте")[user_status["is_muted"]]}\n'  #
              f'Осталось разблоков: {user_status["user_blocks"]}\n\n'
              f'Последний мьют\n'
              f'Причина: {user_last_mute["moderator_message"]}\n'
              f'Чат: @{chat.username}\n'
              f'Админ: @{user_last_mute["admin_username"]}\n'
              f'Дата мьюта: {user_last_mute["date_of_mute"]}')

    await message.answer(text=answer, reply_markup=show_user_keyboard)


async def show_user_deeplink(message: types.Message, admins) -> None:
    dl = '@' + str(message.text).split(' ')[1]  # TODO переписать обработчик без костылей
    await show_user(message, dl=dl, admins=admins)
