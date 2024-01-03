from aiogram import types
from aiogram.exceptions import TelegramBadRequest

from core.config_vars import ConfigVars
from core.config import bot
from core.database_functions.db_functions import *
from core.handlers.privatechat_functions.status import status
from core.utils.restrict import restrict


async def unmute(message: types.Message):
    user_id = message.from_user.id
    chats = ConfigVars.CHATS
    last_mute = await get_last_mute(user_id)
    user_data = await get_user(user_id)
    if last_mute is None:
        await message.answer('Тебя нет в моей базе. Если у тебя сохраняется блокировка, '
                             'обратись к модераторам, например, @deanrie.')
        return

    # для получения инфы о пользователе нужно быть админом группы
    try:
        member = await bot.get_chat_member(chat_id=last_mute['chat_id'], user_id=user_id)
        print('Unmute: ', member)
        if member.status == 'restricted' and member.can_send_messages or member.status == 'member':
            await message.answer('Вы уже разблокированы. Если это не так, обратитесь в поддержку.')
            return
        if member.status in ('administrator', 'creator'):
            await message.answer('Вы админ. Вас нельзя заблокировать.')
            return
    except TelegramBadRequest as e:  # TODO переписать дичь в нормальный обработчик
        print('Ошибка доступа, бот не управляет чатом, в котором прошел мьют', e)
    if user_data['user_blocks'] > 0:
        await db_unmute(user_id)

        for chat in chats:
            try:
                await restrict(user_id, chat, ConfigVars.UNMUTE_SETTINGS)
            except Exception:
                continue
        await status(message)
        return
    await message.answer('К сожалению, у вас закончились разблоки. Теперь вы можете '
                         'остаться в чатах в режиме читателя.')
