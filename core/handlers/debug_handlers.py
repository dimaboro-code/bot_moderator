from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.enums.chat_type import ChatType
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.database_functions.db_functions import delete_user
from core.database_functions.test_db import test_simple_db
from core.filters.admin_filter import AdminFilter
from core.utils.send_report import send_mute_report

debug_router = Router()
debug_router.message.filter(F.chat.type == ChatType.PRIVATE, AdminFilter())


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
async def send_report_handler(message: Message) -> None:
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
    await send_mute_report(user_id, username, admin, chat_username, reason_message)


@debug_router.message(Command('get_chat_id'))
async def get_chat_id_handler(message: Message, bot: Bot):
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
