from aiogram.types import CallbackQuery, Message
from config import bot
import asyncio
from db import add_lives, delete_lives, delete_all_lives, get_id
from system_functions.is_username import is_username
from privatechat_functions.show_user import show_user


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
    await call.answer(show_alert=False, text='Успешно')
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await asyncio.sleep(1)
    msg = Message()
    msg.text = '/show_user @' + username
    msg.from_user = call.message.from_user
    msg.chat = call.message.chat

    await show_user(msg)
