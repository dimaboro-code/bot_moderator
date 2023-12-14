from aiogram.types import CallbackQuery
from core.config import bot
from database_functions.db_functions import add_lives, delete_lives, delete_all_lives, get_id, get_last_mute, get_user
from core.utils.is_username import is_username
from core.keyboards.show_user_keyboard import show_user_keyboard


react_funcs = {
    'add_unblock': add_lives,
    'remove_unblock': delete_lives,
    'remove_all_unblocks': delete_all_lives
}


async def show_user_react(call: CallbackQuery):
    func_query = call.data.split('_')
    real_query = '_'.join(func_query[2:])
    print(real_query)
    username = await is_username(call.message.text)
    print(username)
    user_id = await get_id(username)
    print(user_id)

    await react_funcs[real_query](user_id)
    user_status = await get_user(user_id)
    user_last_mute = await get_last_mute(user_id)
    chat = await bot.get_chat(user_last_mute["chat_id"])

    await call.answer(show_alert=False, text='Успешно')

    updated_text = (
        f'Пользователь: @{username}\n'
        f'Статус: {("без ограничений", "в мьюте")[user_status["is_muted"]]}\n'  # 
        f'Осталось разблоков: {user_status["user_blocks"]}\n\n'
        f'Последний мьют\n'
        f'Причина: {user_last_mute["moderator_message"]}\n'
        f'Чат: @{chat.username}\n'
        f'Админ: @{user_last_mute["admin_username"]}\n'
        f'Дата мьюта: {user_last_mute["date_of_mute"]}'
    )
    print(updated_text)
    await bot.edit_message_text(
        chat_id=call.message.chat.id, message_id=call.message.message_id,
        text=updated_text,
        reply_markup=show_user_keyboard
    )
