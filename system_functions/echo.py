from aiogram.types import Message
from privatechat_functions.show_user import show_user


async def echo(message: Message) -> Message:
    message.text = '@' + message.text.split(' ')[1]
    await show_user(message)
