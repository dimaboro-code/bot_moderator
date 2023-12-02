from aiogram.types import Message
from config import bot


async def send_report(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await bot.send_message(chat_id=-1002065542994,
                           text=f'Мьют {username},\nuser id: {user_id},\n'
                                f'Подробнее: <a href="t.me/testing_projects_42_bot?start={username}">'
                                f'<b>/show_user @{username}</b></a>\nt.me/testing_projects_42_bot?start=@{username}',
                           parse_mode='HTML'
                           )