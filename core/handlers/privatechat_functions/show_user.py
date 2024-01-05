from aiogram import types, Bot

from core.database_functions.db_functions import get_id
from core.keyboards.show_user_keyboard import show_user_keyboard
from core.utils.is_username import is_username
from core.utils.send_report import send_report_to_group
from core.handlers.privatechat_functions.status import status


async def show_user_handler(message: types.Message):
    len_msg = len(message.text.split())
    user_username = message.from_user.username
    chat_username = message.chat.username

    if len_msg < 2:
        answer = 'Некорректная команда. Должна быть /show_user <user_id> или /show_user <@username>.'
        await message.answer(answer)
        return

    user_id = await get_id_from_text(message.text)
    if user_id is None:
        answer = 'Пользователь не найден.'
        await message.answer(answer)
        return

    answer = await status(user_id=user_id)

    try:
        await message.answer(answer, reply_markup=show_user_keyboard)
    except Exception as e:
        await send_report_to_group(user_id=user_id, chat_id='private', chat_username=chat_username,
                                   user_username=user_username, problem=f'Не сработал show_user, ошибка: {e}')


async def get_id_from_text(text: str):
    pure_text: str = text.split()[1]

    if pure_text.isdigit():
        user_id = int(pure_text)
    else:
        username = is_username(pure_text)
        if username is not None:
            pure_text = username
        user_id = await get_id(f'{pure_text}')
    return user_id
