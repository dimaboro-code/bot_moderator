from aiogram import Bot
from core.config_vars import ConfigVars
from ..config import bot as bt


async def send_mute_report(
    user_id: int,
    username: str,
    admin_username: str,
    chat_username: str,
    reason_message: str,
    log_chanel: int = ConfigVars.LOG_CHANNEL,
    bot: Bot = bt,
    **kwargs
):
    """
    Отчет в канал с отчетами
    Args:
        admin_username:
        chat_username:
        reason_message:
        bot:
        user_id:
        username:
        log_chanel:

    Returns:

    """
    if kwargs:
        pass
    await bot.send_message(chat_id=log_chanel,
                           text=f'Мьют @{username},\n'
                                f'user id: {user_id},\n'
                                f'Подробнее: <a href="t.me/{str(ConfigVars.BOT_USERNAME)}?start={user_id}">'
                                f'<b>{username}</b></a>\n\n'
                                f'Чат: @{chat_username}\n'
                                f'Админ: @{admin_username}\n'
                                f'Причина: {reason_message}',
                           parse_mode='HTML', disable_web_page_preview=True
                           )


async def send_bug_report(
    user_id: int,
    chat_id: int | str,
    problem: str | Exception,
    user_username: str | None = None,
    chat_username: str | None = None,
    bot: Bot = bt,
    log_chat: str = ConfigVars.LOG_CHAT,
    **kwargs
):
    if type(problem) is Exception:
        problem = str(problem)
    await bot.send_message(chat_id=log_chat,
                           text=f'Юзер: {user_id}\n'
                                f'Юзер юзернейм: {user_username}\n'
                                f'Чат: {chat_id}\n'
                                f'Чат юзернейм: @{chat_username}\n'
                                f'{problem}',
                           parse_mode='HTML'
                           )
