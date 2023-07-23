from aiogram import types

from config import bot
from config import CHATS

from system_functions.is_username import is_username
from system_functions.show_user_keyboard import show_user_keyboard

from db import get_id
from db import get_user, get_last_mute




async def show_user(message: types.Message):
    moderator_id = message.from_user.id
    is_chat_admin = False

    for chat_id in CHATS:
        moderator: types.ChatMember = await bot.get_chat_member(chat_id=chat_id, user_id=moderator_id)
        moderators = await bot.get_chat_administrators(chat_id)

        if moderator in moderators:
            is_chat_admin = True
            break

    if is_chat_admin is False:
        await message.answer('Вы не являетесь модератором сообщества')
        return

    username = await is_username(message.text)
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
                             f'Осталось разблоков: 3'
                             f'Пользователь не блокировался')

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