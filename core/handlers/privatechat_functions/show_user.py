from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.database_functions.db_functions import get_id
from core.utils.get_username_from_text import is_username
from ..callback_privatechat_functions.callback_show_users import name_alias_keyboard, alias_funcs
from core.utils.send_report import send_bug_report
from core.handlers.privatechat_functions.status import status


async def show_user_handler(message: types.Message, session):
    len_msg = len(message.text.split())
    user_username = message.from_user.username
    chat_username = message.chat.username

    if len_msg < 2:
        answer = 'Некорректная команда. Должна быть /show_user <user_id> или /show_user <@username>.'
        await message.answer(answer)
        return

    user_id = await get_id_from_text(message.text, session)
    if user_id is None:
        answer = 'Пользователь не найден.'
        await message.answer(answer)
        return

    answer = await status(user_id=user_id, session=session)

    try:
        builder: InlineKeyboardBuilder = await name_alias_keyboard(user_id, alias_funcs)
        await message.answer(answer, reply_markup=builder.as_markup())
    except Exception as e:
        await send_bug_report(user_id=user_id, chat_id='private', chat_username=chat_username,
                              user_username=user_username, problem=f'Не сработал show_user, ошибка: {e}')


async def get_id_from_text(text: str, session):
    pure_text: str = text.split()[1]

    if pure_text.isdigit():
        user_id = int(pure_text)
    else:
        username = is_username(pure_text)
        if username is not None:
            pure_text = username
        user_id = await get_id(f'{pure_text}', session)
    return user_id
