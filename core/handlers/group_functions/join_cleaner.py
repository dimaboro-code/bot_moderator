
from aiogram import types

async def join_cleaner(message: types.Message):
    await message.delete()