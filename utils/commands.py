from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='unmute',
            description='Разблокироваться'
        ),
        BotCommand(
            command='status',
            description='Текущее состояние'
        ),
        BotCommand(
            command='help',
            description='Помощь'
        ),
        BotCommand(
            command='get_chat_id',
            description='Узнать ID чата или группы. '
                        'Сразу после команды через пробел пишется юзернейм нужного чата.'
        ),
        BotCommand(
            command='send_report',
            description='отправить отчет'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeAllPrivateChats())