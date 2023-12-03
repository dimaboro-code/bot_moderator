from aiogram import types

from config import bot, CHATS, UNMUTE_SETTINGS

from system_functions.restrict import restrict

from db import *

from privatechat_functions.status import status


async def unmute(message: types.Message):
    user_id = message.from_user.id

    if not await in_database(user_id):
        await message.answer('Тебя нет в моей базе. Если у тебя сохраняется блокировка, обратись к модераторам, например, @deanrie.')
        return

    last_mute = await get_last_mute(user_id)
    user_data = await get_user(user_id)
 
    # для получения инфы о пользователе нужно быть админом группы
    try:
        member = await bot.get_chat_member(chat_id=last_mute['chat_id'], user_id=user_id)
        print(member)
        if member.status == 'restricted' and member.can_send_messages:
            await message.answer('Вы уже разблокированы. Если это не так, обратитесь в поддержку.')
            return
        if member.status in ('administrator', 'creator'):
            await message.answer('Вы админ. Вас нельзя заблокировать.')
            return
    except AttributeError:
        pass
    if user_data['user_blocks'] > 0:
        await db_unmute(user_id)


        for chat in CHATS:
            try:
                await restrict(user_id, chat, UNMUTE_SETTINGS)
            except:
                continue
        await status(message)
    else:
        await message.answer('К сожалению, у вас закончились разблоки. Теперь вы можете остаться в чатах в режиме читателя.')
