from aiogram.filters import BaseFilter
from aiogram.types import Message


class AdminFilter(BaseFilter):
    """
    Фильтр на админа.
    input: message (передает обработчик),
    admin_ids (передается в качестве аргумента, по умолчанию конфиг.админс)
    output: bool
    """

    async def __call__(self, message: Message, admins) -> bool:
        if message.from_user.id in admins:
            return True
        return False
