"""
file for eraser func
"""
from aiogram import types

from core.database_functions.db_functions import delete_row
from core.utils.is_chat_admin import is_chat_admin


async def eraser(message: types.Message):
    """
    func for deleting yourself from database
    only for admins
    :param message: admin send command to bot
    :return: sends message about success
    """
    is_admin = await is_chat_admin(message.from_user.id)
    if not is_admin:
        await message.answer('Вы не являетесь модератором, функция недоступна')
        return

    await delete_row(message.from_user.id)
    await message.answer('Успешно')
