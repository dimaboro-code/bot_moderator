from aiogram import Bot
from core.config import Config, bot as bt


async def send_report_to_channel(
        user_id: int,
        username: str,
        admin: str,
        chat_username: str,
        reason_message: str,
        log_chanel: int = Config.LOG_CHANNEL,
        bot: Bot = bt
):
    """
    Отчет в канал с отчетами
    Args:
        admin:
        chat_username:
        reason_message:
        bot:
        user_id:
        username:
        log_chanel:

    Returns:

    """
    await bot.send_message(chat_id=log_chanel,
                           text=f'Мьют @{username},\n'
                                f'user id: {user_id},\n'
                                f'Подробнее: <a href="t.me/@{str(Config.LOG_CHANNEL_USERNAME)}?start={username}">'
                                f'<b>{username}</b></a>\n\n'
                                f'Чат: @{chat_username}\n'
                                f'Админ: @{admin}\n'
                                f'Причина: {reason_message}',
                           parse_mode='HTML'
                           )


async def send_report_to_group(
        user_id: int,
        user_username: str | None,
        chat_id: int,
        chat_username: str | None,
        problem: str | Exception,
        bot: Bot = bt,
        log_chat: str = Config.LOG_CHAT
):
    """
    отчет об ошибках
    Args:
        user_id:
        user_username:
        chat_id:
        chat_username:
        problem:
        bot:
        log_chat:

    Returns:

    """
    if type(problem) is Exception:
        problem = str(problem)
    await bot.send_message(chat_id=log_chat,
                           text=f'Юзер: {user_id}\n'
                                f'Юзер юзернейм: {user_username}\n'
                                f'Чат: {chat_id}\n'
                                f'Чат юзернейм: @{chat_username}\n'
                                f'Не прошел отчет о мьюте, ошибка: \n{problem}',
                           parse_mode='HTML'
                           )