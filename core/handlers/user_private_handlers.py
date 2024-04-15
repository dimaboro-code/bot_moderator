from aiogram import Router, F, Bot
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from core.services.status import status
from core.services.unmute import unmute

user_private_router = Router()
user_private_router.message.filter(F.chat.type == ChatType.PRIVATE)


@user_private_router.message(CommandStart())
async def send_welcome(message: Message, session, bot: Bot):
    hello_message = (
        f'Привет!\n\n'
        f'Раз ты тут, то, наверное, тебя лишили голоса (замьютили) в чатах проекта @slashdesigner. '
        f'Мьют в одном чате действует во всех наших чатах сразу.\n'
        f'Я помогу тебе разблокироваться, только прочитай перед этим наши правила, '
        f'чтобы избежать новых блокировок в будущем.\n\n'
        f'@figmachat        <a href="https://slashdesigner.ru/figmachat">Правила</a>\n'
        f'@designchat2     <a href="https://slashdesigner.ru/designchat">Правила</a>\n'
        f'@whatthefontt    <a href="https://slashdesigner.ru/whatthefont">Правила</a>\n'
        f'@systemschat     <a href="http://slashd.ru/systemschat">Правила</a>\n\n'
        f'У каждого участника чатов есть 3 разблока — возможности вернуть голос во всех чатах. '
        f'После третьего мьюта нам придётся навсегда оставить тебя в режиме читателя.'
    )
    await message.answer(hello_message, parse_mode='HTML', disable_web_page_preview=True)
    await bot_help(message)
    status_message = await status(message.from_user.id, session, bot)
    await message.answer(status_message)


@user_private_router.message(Command('help'))
async def bot_help(message: Message):
    # TODO переписать в нормальный вид
    """
    :param message:
    :return:
    """
    text = ('Доступные команды\n\n'
            '/start - запустить бота\n'
            '/status - текущее состояние\n'
            '/unmute - разблокироваться\n'
            '/help - список доступных команд\n')
    await message.answer(text, reply_markup=ReplyKeyboardRemove())


@user_private_router.message(Command('status'))
async def status_handler(message: Message, session, bot: Bot):
    """
     start func
    :param message:
    :return:
    """
    user_id = message.from_user.id

    answer = await status(user_id=user_id, session=session, bot=bot)

    await message.answer(answer)


@user_private_router.message(Command('unmute'))
async def unmute_handler(message: Message, bot: Bot, session):
    user_id = message.from_user.id
    success, answer = await unmute(user_id=user_id, bot=bot, session=session)
    if success:
        await message.answer('Успешно')
        await message.answer(answer)
    else:
        await message.answer(answer)
