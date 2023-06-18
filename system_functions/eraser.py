
from aiogram import types

from db import delete_row

async def eraser(message: types.Message):
    await delete_row(message.from_user.id)