from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.enums.chat_type import ChatType
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.database_functions.db_functions import add_lives, delete_lives, delete_all_lives
from core.filters.admin_filter import AdminFilter
from core.handlers.callback_privatechat_functions.callback_show_users import name_alias_keyboard
from core.handlers.privatechat_functions.show_user import get_id_from_text
from core.handlers.privatechat_functions.status import status
from core.models.data_models import AdminFunctions
from core.utils.send_report import send_bug_report

admin_private_router = Router()
admin_private_router.message.filter(F.chat.type == ChatType.PRIVATE, AdminFilter())

react_funcs = {
    'add_unblock': add_lives,
    'remove_unblock': delete_lives,
    'remove_all_unblocks': delete_all_lives
}

alias_funcs = {
    'Добавить 1 разблок': 'add_unblock',
    'Удалить 1 разблок': 'remove_unblock',
    'Удалить все разблоки': 'remove_all_unblocks',
}


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
        await send_bug_report(user_id=user_id, chat_id='private', chat_username=chat_username,
                              user_username=user_username, problem=f'Не сработал show_user, ошибка: {e}')


@admin_private_router.callback_query(AdminFunctions.filter())
async def show_user_react(call: CallbackQuery, callback_data: AdminFunctions, session, bot: Bot):
    user_id = callback_data.user_id
    await react_funcs[callback_data.function](user_id, session=session)
    updated_text = await status(user_id, session)
    builder: InlineKeyboardBuilder = await name_alias_keyboard(user_id, alias_funcs)
    await bot.edit_message_text(
        chat_id=call.message.chat.id, message_id=call.message.message_id,
        text=updated_text,
        reply_markup=builder.as_markup()
    )
    await call.answer(show_alert=False, text='Успешно')
