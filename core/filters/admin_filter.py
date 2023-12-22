from typing import List
from aiogram.filters import BaseFilter
from aiogram.types import Message
from core.config import Config


class AdminFilter(BaseFilter):
    """
    Фильтр на админа.
    input: message (передает обработчик),
    admin_ids (передается в качестве аргумента, по умолчанию конфиг.админс)
    output: bool
    """
    async def __call__(self, message: Message, admin_ids: List[int] = Config.ADMINS) -> bool:
        if message.from_user.id in admin_ids:
            return True
        return False
