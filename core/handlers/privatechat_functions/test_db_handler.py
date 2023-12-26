from aiogram.types import Message

from core.database_functions.test_db import test_simple_db


async def test_db_handler(message: Message) -> None:
    test_result = await test_simple_db()
    await message.answer(f'Тесты {("не пройдены", "пройдены успешно")[test_result]}\n'
                         f'Детали смотри в логах сервера')
