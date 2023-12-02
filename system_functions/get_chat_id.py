from aiogram import types
from config import bot
from aiogram.utils.exceptions import MessageTextIsEmpty


async def get_chat_id(message: types.Message):
    chat_ids = []
    try:
        text = message.text.strip().split()
    except MessageTextIsEmpty:
        await message.answer('Не указан username чата, повторите команду и после пробела напишите username')
        return
    text.pop(0)
    answer = ''
    for chat in text:
        # print(chat)
        chat_id = await bot.get_chat(chat)
        chat_ids.append(str(chat_id.id))
        answer = ' '.join(chat_ids)
        answer = '<code>' + answer + '</code>'
    await message.answer(answer, parse_mode='HTML')
