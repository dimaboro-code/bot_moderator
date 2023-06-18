from aiogram import types

async def testfunc(message: types.Message):
    await message.answer("Функция /testfunc сработала")