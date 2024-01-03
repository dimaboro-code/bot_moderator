from aiogram import types, Bot

from core.database_functions.db_functions import get_id, get_username
from core.database_functions.db_functions import get_user, get_last_mute
from core.keyboards.show_user_keyboard import show_user_keyboard
from core.utils.is_username import is_username
from core.utils.send_report import send_report_to_group


async def show_user_handler(message: types.Message, bot: Bot):
    len_msg = len(message.text.split())
    user_id = None
    answer = ''

    if len_msg < 2:
        answer = 'Некорректная команда. Должна быть /show_user <user_id> или /show_user <@username>.'
    else:
        user_id = await get_id_from_text(message.text)

    if user_id is None:
        answer = 'Пользователь не найден.'

    else:
        username = await get_username(user_id=user_id)
        show = await show_user(user_id=user_id, chat_id=message.chat.id, bot=bot, username=username)
        if show:
            answer = False

    if answer:
        await message.answer(answer)


async def show_user(user_id: int, chat_id: int, username: str, bot: Bot):
    user_status = await get_user(user_id)
    user_last_mute = None
    chat: types.Chat | None = None

    if user_status is not None:
        user_last_mute = await get_last_mute(user_id)

    if user_last_mute is not None:
        chat: types.Chat = await bot.get_chat(user_last_mute["chat_id"])

    if user_status is None or user_last_mute is None:
        answer = f'Пользователь: @{username}\n' \
                 'Статус: без ограничений\n' \
                 f'Осталось разблоков: {user_status["user_blocks"] if user_status else 3}\n' \
                 'Пользователь ранее не блокировался'

    else:
        if chat is None:
            await send_report_to_group(user_id=user_id, chat_id=chat_id, chat_username=None, user_username=None,
                                       problem=f'show_user, Нет доступа к чату {user_last_mute["chat_id"]}')
        answer = (f'Пользователь: @{username}\n'
                  f'Статус: {("без ограничений", "в мьюте")[user_status["is_muted"]]}\n'  #
                  f'Осталось разблоков: {user_status["user_blocks"]}\n\n'
                  f'Последний мьют\n'
                  f'Причина: {user_last_mute["moderator_message"]}\n'
                  f'Чат: @{chat.username}\n'
                  f'Админ: @{user_last_mute["admin_username"]}\n'
                  f'Дата мьюта: {user_last_mute["date_of_mute"]}')

    try:
        await bot.send_message(chat_id=chat_id, text=answer, reply_markup=show_user_keyboard)
        return True
    except Exception as e:
        await send_report_to_group(user_id=user_id, chat_id=chat_id, chat_username=None, user_username=None,
                                   problem=f'Не сработал show_user, ошибка: {e}')
        return False


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
