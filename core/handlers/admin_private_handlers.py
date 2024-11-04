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
from core.services.status import status, status_log
from core.services.unmute import admin_unmute
from core.utils.restrict import restrict
from core.utils.send_report import send_bug_report
from core.utils.text_checks import get_id_from_text
from core.utils.get_username_from_text import get_status_from_text

admin_private_router = Router()
admin_private_router.message.filter(F.chat.type == ChatType.PRIVATE, AdminFilter())


async def back(*args, **kwargs):
    pass

react_funcs = {
    'add_unblock': add_lives,
    'remove_unblock': delete_lives,
    'remove_all_unblocks': delete_all_lives,
    'unblock': admin_unmute,
    'mute': mute,
    'mute_story': status_log,
    'back': back
}

alias_funcs = {
    'Добавить 1 разблок': 'add_unblock',
    'Удалить 1 разблок': 'remove_unblock',
    'Удалить все разблоки': 'remove_all_unblocks',
    'Разблокировать': 'unblock',
    'Заблокировать': 'mute',
    'Показать историю мьютов': 'mute_story'
}


@admin_private_router.message(Command('admin_unmute'))
async def real_admin_unmute(message: Message, bot: Bot):
    user_id = await get_id_from_text(message.text)
    if user_id is None:
        print('баг, нет айди')
        raise ValueError('no id in text')
    restriction = await restrict(user_id=user_id, chat_id_orig=user_id, bot=bot, chats=ConfigVars.CHATS,
                                 permissions=ConfigVars.UNMUTE_SETTINGS)
    # если разблок не прошел
    if restriction is False:
        answer = 'Не удалось разблокировать, отчет направлен разработчику. Обратитесь к модераторам, например, @deanrie'
        await message.answer(answer)
    else:
        await message.answer('Успешно')


@admin_private_router.message(Command('status'), F.text.len() > 10)
@admin_private_router.message(CommandStart(deep_link=True), F.text.len() < 21)
async def admin_status_handler(message: Message, bot: Bot):
    len_msg = len(message.text.split())
    user_username = message.from_user.username
    chat_username = message.chat.username

    if len_msg < 2:
        answer = 'Некорректная команда. Должна быть /status <user_id> или /status <@username>.'
        await message.answer(answer)
        return

    user_id = await get_id_from_text(message.text)
    if user_id is None:
        answer = 'Пользователь не найден.'
        await message.answer(answer)
        return

    answer = await status(user_id=user_id, bot=bot)
    current_status = get_status_from_text(answer)

    try:
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
                              user_username=user_username, problem=f'Не сработал show_user, ошибка: {e}', bot=bot)


@admin_private_router.callback_query(AdminFunctions.filter())
async def admin_funcs_callback(call: CallbackQuery, callback_data: AdminFunctions, bot: Bot, admins: list[int]):
    user_id = callback_data.user_id
    match callback_data.function:
        case 'unblock':
            if user_id in admins:
                await call.answer(show_alert=True, text='Это вообще как? Напиши, как у тебя получилось улететь в блок :)')
            success, updated_text = await react_funcs[callback_data.function](user_id, bot)
            if not success:
                await call.answer(text=updated_text, show_alert=True)
                return
        case 'mute':
            if user_id in admins:
                await call.answer(show_alert=True, text='админы не блокируются даже через консоль :)')
                return
            data = UserData()
            data.parse_message(call.message, user_id=user_id)
            data.chat_id = ConfigVars.CHATS[0]
            last_mute = await get_last_mute(user_id)
            data.reason_message = last_mute['moderator_message']
            success = await mute(data=data, bot=bot)
            if not success:
                await call.answer(text='Мьют не прошел, отчет направлен разработчику', show_alert=True)
                return
            updated_text = await status(user_id, bot)
        case 'mute_story':
            updated_text = await react_funcs[callback_data.function](user_id, bot)
            builder = InlineKeyboardBuilder()
            builder.button(
                text='Скрыть историю мьютов',
                callback_data=AdminFunctions(function='back', user_id=user_id)
            )
            await bot.edit_message_text(
                chat_id=call.message.chat.id, message_id=call.message.message_id,
                text=updated_text,
                reply_markup=builder.as_markup()
            )
            await call.answer(show_alert=False, text='Успешно')
            return
        case _:
            await react_funcs[callback_data.function](user_id)
            updated_text = await status(user_id, bot)
    current_status = get_status_from_text(updated_text)
    builder = InlineKeyboardBuilder()
    for button, func in alias_funcs.items():
        if func == 'mute' and current_status == 'в мьюте':
            continue
        if func == 'unblock' and current_status == 'без ограничений':
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
