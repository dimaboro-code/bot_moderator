from aiogram.types import Message

from core.utils.send_report import send_mute_report


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
