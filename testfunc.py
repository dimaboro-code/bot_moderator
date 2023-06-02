from aiogram import types


async def testfunc(message: types.Message):
    await message.answer("тест")