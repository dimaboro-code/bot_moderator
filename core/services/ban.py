from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core import ConfigVars
from core.models.data_models import BanHammer


async def ban_name(user_to_ban: int, bot: Bot):
    success = False
    for chat in ConfigVars.CHATS:
        success = await bot.ban_chat_member(chat_id=chat, user_id=user_to_ban, until_date=10, revoke_messages=True)
        if not success:
            await bot.send_message(chat_id=ConfigVars.LOG_CHAT, text=f'Бан не прошел. Пользователь {user_to_ban}'
                                                                     f', чат {chat}\n')
    return success


def get_bh_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Забанить',
        callback_data=BanHammer(user_id=user_id, function='ban_first'),
    )
    builder.adjust(1, repeat=True)
    return builder
