
# direct import of async lib IO
# it is needed for delete_message()
import asyncio

# types – our object models, like Message or Chat
from aiogram import types

# all actions logger, currently doesn't exist
import logging

# run webhook
from aiogram.utils.executor import start_webhook

# settings import
from config import bot, dp, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, CHATS, MESSAGES_FOR_DELETE, MUTE_SETTINGS, UNMUTE_SETTINGS

# full database import
from db import *

from group_functions.mute import mute


# Configure logging
logging.basicConfig(level=logging.INFO)

# webhook control
async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await database.connect()

# stopping app
async def on_shutdown(dispatcher):
    await database.disconnect()
    await bot.delete_webhook()





# DELETE MESSAGE





@dp.message_handler(commands=['delete_user'])

async def delete_user(message: types.Message):
    await delete_row(message.from_user.id)




# GROUP CHAT FUNCTIONS

dp.register_message_handler(mute, commands=['mute'], is_chat_admin=True, commands_prefix='!/')


#ADD UNBLOCKS

@dp.message_handler(commands=['add_unblocks'],  is_chat_admin=True, commands_prefix='!/')

async def add_unblocks(message: types.Message):
    user_id = message.reply_to_message.from_user.id
    lives = int(message.text[14:]) if len(str(message.text)) >= 15 else 1
    await add_lives(user_id, lives)
    await message.delete()


# JOIN CLEANER

@dp.message_handler(content_types=MESSAGES_FOR_DELETE)
async def delete_messages(message: types.Message):
    await message.delete()


# PRIVATE CHAT FUNCTIONS 


# /start

@dp.message_handler(commands=['start'], chat_type='private')
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


@dp.message_handler(commands=['status'], chat_type='private')
async def status(message: types.Message):
    ''' start func
    :param message:
    :return:
    '''
    user_id = message.from_user.id

    is_in_database = await in_database(user_id=user_id)

    if not is_in_database:
        await message.answer('Статус: У вас осталось 3 разблока.')
        return None

    last_mute = await get_last_mute(user_id)

    if last_mute is None:
        await message.answer('Нет данных о мьюте')
    else:
        chat = await bot.get_chat(last_mute["chat_id"])

    user_data = await get_user(user_id)

    # reason_to_mute = await bot.get_message(chat_id=last_mute["chat_id"], message_id=last_mute["message_id"])
    answer = (f'Статус\n'
 
              f'Текущее состояние: {("разблокирован", "заблокирован")[user_data["is_muted"]]}\n' 
              f'Осталось разблокировок: {user_data["user_blocks"]}\n\n' 
              f'Последний мьют\n'
              f'Причина: {last_mute["moderator_message"]}\n' 
              f'Чат: {chat.username}\n' 
              f'Админ: {last_mute["admin_username"]}\n' 
              # f'Сообщение: {reason_to_mute.text}\n' 
              f'Дата мьюта: {last_mute["date_of_mute"]}')
    # await delete_message(reason_to_mute)
    await message.answer(answer)


@dp.message_handler(commands=['help'], chat_type='private', state='*')
async def bot_help(message: types.Message):
    """
    :param message:
    :return:
    """
    text = 'Доступные команды\n\n'
    text += '/start - запустить бота\n'
    text += '/unmute - разблокироваться\n'
    text += '/help - список доступных команд\n'
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['chat_id'], chat_type='private')
async def get_chat_id(message: types.Message):
    chat_ids = []
    text = message.text.strip().split()
    text.pop(0)
    answer = None
    for chat in text:
        print(chat)
        chat_id = await bot.get_chat(chat)
        chat_ids.append(str(chat_id.id))
        answer = ' '.join(chat_ids)
    await message.answer(answer)


# UNMUTE

@dp.message_handler(chat_type='private', commands=['unmute'], commands_prefix='!/')
async def unmute(message: types.Message):
    user_id = message.from_user.id

    if not await in_database(user_id):
        await message.answer('Вы вне системы. Совершите противоправное действие, чтобы стать частью')
        return

    last_mute = await get_last_mute(user_id)
    user_data = await get_user(user_id)
 
    # для получения инфы о пользователе нужно быть админом группы
    try:
        member = await bot.get_chat_member(chat_id=last_mute['chat_id'], user_id=user_id)
        print(member)
        if member.can_send_messages is True:
            await message.answer('Вы уже разблокированы. Если это не так, обратитесь в поддержку.')
            return
    except AttributeError:
        pass
    if user_data['user_blocks'] > 0:
        await db_unmute(user_id)



        for chat in CHATS:
            await restrict(user_id, chat, UNMUTE_SETTINGS)
        await status(message)
    else:
        await message.answer('У вас закончились разблоки.')


if __name__ == '__main__':

    # start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
