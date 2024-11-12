import asyncio

from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums import MessageEntityType

from core.utils.create_redis_pool import get_conn


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
        'вопрос',
        'тема',
        'ревью'
    ]

    async def __call__(self, message: Message) -> bool:
        allow = False
        if message.reply_to_message:
            print('реплей')
            allow = True
        elif message.entities is not None:
            for entity in message.entities:
                if entity.type == MessageEntityType.HASHTAG:
                    print('с хэштегом')
                    hashtag = message.text[entity.offset+1:(entity.offset + entity.length)].lower()
                    if hashtag in self.allowed_hashtags:
                        allow = True
        elif message.caption_entities is not None:
            for entity in message.caption_entities:
                if entity.type == MessageEntityType.HASHTAG:
                    print('с хэштегом')
                    hashtag = message.caption[entity.offset+1:(entity.offset + entity.length)].lower()
                    if hashtag in self.allowed_hashtags:
                        allow = True
        if allow and message.media_group_id:
            async with get_conn() as redis:
                redis_key = f'media_group_id:{message.from_user.id}'
                await redis.set(redis_key, message.media_group_id, ex=600)
        if not allow and message.media_group_id:
            print('медиа группа')
            await asyncio.sleep(1)
            async with get_conn() as redis:
                redis_key = f'media_group_id:{message.from_user.id}'
                redis_value = await redis.get(redis_key)
            if int(redis_value) == int(message.media_group_id):
                allow = True
        return allow


class StrictChatFilter(BaseFilter):
    """
    Отделяет чаты, в которых должен работать хэндлер от тех, где не должен
    """
    async def __call__(self, message: Message, chat_settings: dict) -> bool:
        strict_chats = chat_settings.get('strict_chats', [])
        if message.chat.id in strict_chats:
            return True
        return False
