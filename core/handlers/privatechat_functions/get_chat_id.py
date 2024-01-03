from aiogram import types

from core.config import bot


async def get_chat_id_handler(message: types.Message):
    if len(message.text.split()) == 1:
        await message.answer('Не указан username группы или канала')
        return
    chat_ids = []
    text = message.text.strip().split()
    text.pop(0)
    answer = ''
    for chat in text:
        chat_id = await bot.get_chat(chat)
        chat_ids.append(str(chat_id.id))
        answer = ' '.join(chat_ids)
    await message.answer(answer)
