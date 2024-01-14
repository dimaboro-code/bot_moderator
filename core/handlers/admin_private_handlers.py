from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.enums.chat_type import ChatType
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.filters.admin_filter import AdminFilter
from core.handlers.callback_privatechat_functions.callback_show_users import name_alias_keyboard, alias_funcs
from core.handlers.privatechat_functions.show_user import get_id_from_text
from core.handlers.privatechat_functions.status import status
from core.utils.send_report import send_report_to_group

admin_private_router = Router()
admin_private_router.message.filter(F.chat.type == ChatType.PRIVATE, AdminFilter())


@admin_private_router.message(Command('show_user'), CommandStart(deep_link=True))
async def show_user_handler(message: Message, session):
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
        await send_report_to_group(user_id=user_id, chat_id='private', chat_username=chat_username,
                                   user_username=user_username, problem=f'Не сработал show_user, ошибка: {e}')
