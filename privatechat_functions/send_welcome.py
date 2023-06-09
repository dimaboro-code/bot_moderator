from aiogram import types

from privatechat_functions.status import status
from privatechat_functions.bot_help import bot_help


async def send_welcome(message: types.Message):
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
    await status(message)