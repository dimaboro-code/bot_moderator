from aiogram.types import Message
from config import bot, LOG_CHANNEL


async def send_report(message: Message) -> None:
    """
    Данная функция создана для отладки, возможно, станет полноценной частью функционала.
    :param message:
    :return: None
    """
    user_id = message.from_user.id
    username = message.from_user.username
    await bot.send_message(chat_id=LOG_CHANNEL,
                           text='Тестовое сообщение!\n'
                                f'Мьют {username},\nuser id: {user_id},\n'
                                f'Подробнее: <a href="t.me/slashdbot?start={username}">'
                                f'<b>{username}</b></a>\n'
                                f'Ccылка: t.me/slashdbot?start=@{username}',
                           parse_mode='HTML'
                           )
