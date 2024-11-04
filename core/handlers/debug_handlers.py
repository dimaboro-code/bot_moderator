from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, Chat

from core import ConfigVars
from core.database_functions.db_functions import delete_user, db_load_chats
from core.database_functions.test_db import test_simple_db
from core.filters.admin_filter import AdminFilter
from core.utils.send_report import send_mute_report

debug_router = Router()
debug_router.message.filter(AdminFilter())


@debug_router.message(Command('test_db'))
async def test_db_handler(message: Message) -> None:
    test_result = await test_simple_db()
    await message.answer(f'Тесты {("не пройдены", "пройдены успешно")[test_result]}\n'
                         f'Детали смотри в логах сервера')


@debug_router.message(Command('eraser'))
async def eraser(message: Message):
    """
    func for deleting yourself from database
    only for admins
    :param message: admin send command to bot
    :return: sends message about success
    """
    await delete_user(message.from_user.id)
    await message.answer('Успешно')


@debug_router.message(Command('send_report'))
async def send_report_handler(message: Message, bot: Bot) -> None:
    """
    Данная функция создана для отладки, возможно, станет полноценной частью функционала.
    :param message:
    :return: None
    """
    user_id = message.from_user.id
    username = message.from_user.username
    admin = 'test_admin'
    chat_username = 'test_chat'
    reason_message = 'test reason'
    await send_mute_report(user_id, username, admin, chat_username, reason_message, bot=bot)


@debug_router.message(Command('get_chat_id'))
async def get_chat_id_handler(message: Message, bot: Bot):
    if len(message.text.split()) == 1:
        await message.answer(f'Id текущего чата: {message.chat.id}')
        return
    chat_ids = []
    text = message.text.strip().split()
    text.pop(0)
    for chat in text:
        chat_id = await bot.get_chat(chat)
        chat_ids.append(str(chat_id.id))
    answer = ' '.join(chat_ids)
    await message.answer(answer)


@debug_router.message(Command('load_chats'))
async def load_chats(message: Message, bot: Bot) -> None:
    chats_for_db = []
    for chat_id in ConfigVars.CHATS:
        chat: Chat = await bot.get_chat(chat_id)
        chats_for_db.append(chat)
    await db_load_chats(chats_for_db)
    await message.answer('Успешно')
