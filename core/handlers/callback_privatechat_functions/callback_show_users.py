from aiogram.types import CallbackQuery

from core.config import bot
from core.database_functions.db_functions import add_lives, delete_lives, delete_all_lives, get_id
from core.handlers.privatechat_functions.status import status
from core.keyboards.show_user_keyboard import show_user_keyboard
from core.utils.is_username import is_username

react_funcs = {
    'add_unblock': add_lives,
    'remove_unblock': delete_lives,
    'remove_all_unblocks': delete_all_lives
}


async def show_user_react(call: CallbackQuery, session):
    func_query = call.data.split('_')
    real_query = '_'.join(func_query[2:])
    username = is_username(call.message.text)
    user_id = None
    word_list = call.message.text.split()  # вынести в отдельную функцию, а лучше переписать коллбэк
    for index, word in enumerate(word_list):
        if word == 'id:':
            user_id = int(word_list[index + 1][:-1])
            break
    if user_id is None:
        user_id = await get_id(username, session)

    await react_funcs[real_query](user_id, session=session)
    updated_text = await status(user_id, session)
    await bot.edit_message_text(
        chat_id=call.message.chat.id, message_id=call.message.message_id,
        text=updated_text,
        reply_markup=show_user_keyboard
    )
    await call.answer(show_alert=False, text='Успешно')
