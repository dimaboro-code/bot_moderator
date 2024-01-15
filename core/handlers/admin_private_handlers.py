from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.enums.chat_type import ChatType
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core import ConfigVars
from core.database_functions.db_functions import add_lives, delete_lives, delete_all_lives, get_last_mute
from core.filters.admin_filter import AdminFilter
from core.models.data_models import AdminFunctions, UserData
from core.services.mute import mute
from core.services.status import status
from core.services.unmute import unmute
from core.utils.keyboards.name_alias_keyboard import name_alias_keyboard
from core.utils.send_report import send_bug_report
from core.utils.text_checks import get_id_from_text
from core.utils.get_username_from_text import get_status_from_text

admin_private_router = Router()
admin_private_router.message.filter(F.chat.type == ChatType.PRIVATE, AdminFilter())

react_funcs = {
    'add_unblock': add_lives,
    'remove_unblock': delete_lives,
    'remove_all_unblocks': delete_all_lives,
    'unblock': unmute,
    'mute': mute
}

alias_funcs = {
    'Добавить 1 разблок': 'add_unblock',
    'Удалить 1 разблок': 'remove_unblock',
    'Удалить все разблоки': 'remove_all_unblocks',
    'Разблокировать': 'unblock',
    'Заблокировать': 'mute'
}


@admin_private_router.message(Command('show_user'))
@admin_private_router.message(CommandStart(deep_link=True))
async def show_user_handler(message: Message, session, bot: Bot):
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

    answer = await status(user_id=user_id, session=session, bot=bot)
    current_status = get_status_from_text(answer)

    try:
        # TODO переписать на свежую голову
        builder = InlineKeyboardBuilder()
        for button, func in alias_funcs.items():
            if func == 'mute':
                if current_status == 'в мьюте':
                    continue
            if func == 'unblock':
                if current_status == 'без ограничений':
                    continue
            builder.button(
                text=button,
                callback_data=AdminFunctions(function=func, user_id=user_id)
            )
        builder.adjust(1, repeat=True)

        await message.answer(answer, reply_markup=builder.as_markup())
    except Exception as e:
        await send_bug_report(user_id=user_id, chat_id='private', chat_username=chat_username,
                              user_username=user_username, problem=f'Не сработал show_user, ошибка: {e}')


@admin_private_router.callback_query(AdminFunctions.filter())
async def show_user_react(call: CallbackQuery, callback_data: AdminFunctions, session, bot: Bot):
    user_id = callback_data.user_id
    if callback_data.function == 'unblock':
        success, updated_text = await react_funcs[callback_data.function](user_id, bot, session=session)
        if not success:
            await call.answer(text=updated_text, show_alert=True)
            return
    elif callback_data.function == 'mute':
        data = UserData()
        data.parse_message(call.message, user_id=user_id)
        data.chat_id = ConfigVars.CHATS[0]
        last_mute = get_last_mute(user_id, session)
        data.reason_message = last_mute['moderator_message']
        success = await mute(data=data, bot=bot, session=session)
        if not success:
            await call.answer(text='Мьют не прошел, отчет направлен разработчику', show_alert=True)
            return
        updated_text = await status(user_id, session, bot)
    else:
        await react_funcs[callback_data.function](user_id, session=session)
        updated_text = await status(user_id, session, bot)

    current_status = get_status_from_text(updated_text)
    print('статус: ', current_status)
    builder = InlineKeyboardBuilder()
    for button, func in alias_funcs.items():
        if func == 'mute':
            if current_status == 'в мьюте':
                continue
        if func == 'unblock':
            if current_status == 'без ограничений':
                continue
        builder.button(
            text=button,
            callback_data=AdminFunctions(function=func, user_id=user_id)
        )
    builder.adjust(1, repeat=True)

    await bot.edit_message_text(
        chat_id=call.message.chat.id, message_id=call.message.message_id,
        text=updated_text,
        reply_markup=builder.as_markup()
    )
    await call.answer(show_alert=False, text='Успешно')
