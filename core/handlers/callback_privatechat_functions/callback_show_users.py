from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core import ConfigVars
from core.database_functions.db_functions import add_lives, delete_lives, delete_all_lives
from core.handlers.privatechat_functions.status import status
from core.models.data_models import AdminFunctions

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


async def name_alias_keyboard(user_id: int, funcs: dict) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for button, func in funcs.items():
        builder.button(
            text=button,
            callback_data=AdminFunctions(function=func, user_id=user_id)
        )
    builder.adjust(1, repeat=True)
    return builder
