from aiogram import types

async def bot_help(message: types.Message):
    """
    :param message:
    :return:
    """
    text = 'Доступные команды\n\n'
    text += '/start - запустить бота\n'
    text += '/unmute - разблокироваться\n'
    text += '/help - список доступных команд\n'
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())