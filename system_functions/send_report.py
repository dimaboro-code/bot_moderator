from aiogram.types import Message
from config import bot


async def send_report(message: Message) -> None:
    """
    Данная функция создана для отладки, возможно, станет полноценной частью функционала.
    :param message:
    :return: None
    """
    user_id = message.from_user.id
    username = message.from_user.username
    await bot.send_message(chat_id=-1001838011289,
                           text='Тестовое сообщение!'
                                f'Мьют {username},\nuser id: {user_id},\n'
                                f'Подробнее: <a href="t.me/slashdbot?start={username}">'
                                f'<b>{username}</b></a>\n'
                                f'Ccылка: t.me/testing_projects_42_bot?start=@{username}',
                           parse_mode='HTML'
                           )
