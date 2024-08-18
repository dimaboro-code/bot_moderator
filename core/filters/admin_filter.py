from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums import MessageEntityType


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


class HashTagFilter(BaseFilter):
    """
    Фильтр на Хэштег в сообщении.
    input: message (передает обработчик),
    output: bool
    """
    allowed_hashtags = [
        'годнота',
        'вопрос'
    ]

    async def __call__(self, message: Message) -> bool:
        if message.reply_to_message:
            print('реплей')
            return True
        if message.entities is not None :
            for entity in message.entities:
                if entity.type == MessageEntityType.HASHTAG:
                    print('с хэштегом')
                    hashtag = message.text[entity.offset+1:(entity.offset + entity.length)].lower()
                    if hashtag in self.allowed_hashtags:
                        return True
        return False


class StrictChatFilter(BaseFilter):
    """
    Отделяет чаты, в которых должен работать хэндлер от тех, где не должен
    """
    async def __call__(self, message: Message, strict_chats: list) -> bool:
        if message.chat.id in strict_chats:
            return True
        return False
