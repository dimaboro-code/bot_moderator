from aiogram import types
from config import bot


async def get_chat_id(message: types.Message):
    chat_ids = []
    text = message.text.strip().split()
    text.pop(0)
    answer = None
    for chat in text:
        # print(chat)
        chat_id = await bot.get_chat(chat)
        chat_ids.append(str(chat_id.id))
        answer = ' '.join(chat_ids)
    await message.answer(answer)
