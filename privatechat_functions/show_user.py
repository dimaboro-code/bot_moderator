from aiogram import types

from config import bot

from system_functions.is_username import is_username
from system_functions.show_user_keyboard import show_user_keyboard
from system_functions.is_chat_admin import is_chat_admin

from db import get_id
from db import get_user, get_last_mute


async def show_user(message: types.Message):
    admin_id = message.from_user.id

    is_admin = await is_chat_admin(admin_id)
    if is_admin is False:
        await message.answer('Вы не являетесь модератором сообщества')
        return

    username = await is_username(message.text)
    print('юзернейм из сообщения:', username)
    if username is None:
        await message.answer('Не указан username')
        return

    user_id = await get_id(username)
    print('юзер айди из базы:', user_id)
    if user_id is None:
        await message.answer('Пользователя нет в базе данных айди')
        return

    user_status = await get_user(user_id)
    print('Инфа о пользователе из базы мьютов:', user_status)
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
              f'Чат: {chat.username}\n'
              f'Админ: {user_last_mute["admin_username"]}\n'
              f'Дата мьюта: {user_last_mute["date_of_mute"]}')

    await message.answer(text=answer, reply_markup=show_user_keyboard)
