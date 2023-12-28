from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from core.database_functions.test_db import test_simple_db


async def test_db_handler(message: Message, session: AsyncSession) -> None:
    test_result = await test_simple_db(session=session)
    await message.answer(f'Тесты {("не пройдены", "пройдены успешно")[test_result]}\n'
                         f'Детали смотри в логах сервера')
