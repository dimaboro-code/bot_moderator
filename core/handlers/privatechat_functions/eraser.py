"""
file for eraser func
"""
from aiogram import types

from core.database_functions.db_functions import delete_user


async def eraser(message: types.Message):
    """
    func for deleting yourself from database
    only for admins
    :param message: admin send command to bot
    :return: sends message about success
    """
    await delete_user(message.from_user.id)
    await message.answer('Успешно')
