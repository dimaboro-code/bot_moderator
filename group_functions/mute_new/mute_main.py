from aiogram import types

from config import bot, CHATS, MUTE_SETTINGS

from system_functions.delete_message import delete_message
from system_functions.restrict import restrict
from .mute_checks import checks
from db import *


async def mute(moderator_message: types.Message):
    """
    Функция для выполнения команды /mute и мьюта пользователя.

    Args:
        moderator_message: Объект types.Message с сообщением модератора.

    """

    permission = await checks(moderator_message)
    if permission[0] is False:
        answer_message = await moderator_message.reply(permission[1])
        await delete_message(answer_message, 2)
        await delete_message(moderator_message)
        return

    elif permission[0] is True:
        user_id = permission[1]

    else:
        print('Вообще в душе не ебу, что может произойти, чтобы выполнилась эта ветка')
        return

    bad_user: types.ChatMember = await bot.get_chat_member(moderator_message.chat.id, user_id)
    username = bad_user.user.username

    for chat_id in CHATS:
        try:
            chat: types.Chat = await bot.get_chat(chat_id)
        except Exception as e:
            await bot.send_message(
                chat_id=-1001868029361,
                text=f'Чат с ID {chat_id} сука не найден, ошибка {e}'
            )
        try:
            await restrict(user_id, chat_id, MUTE_SETTINGS)
            print(chat.username, ': успешно')
        except Exception as e:  # create exception like RestrictError
            print(chat_id, ': ошибка', e)
            await bot.send_message(
                chat_id=-1001868029361,
                text=f'Юзер: {user_id}\n'
                     f'Чат ID: {chat_id}\n'
                     f'Не прошел мьют, ошибка: {e}'
            )
            continue

    check_mute = await bot.get_chat_member(chat_id=moderator_message.chat.id, user_id=user_id)
    if check_mute.status != 'restricted' or check_mute.can_send_messages:
        ans = await moderator_message.answer('Мьют не прошел, отчет направлен разрабу')
        await delete_message(ans, 1)
        await delete_message(moderator_message)
        return

    if not await in_database(user_id):
        await add_user(user_id)

    if moderator_message.reply_to_message:
        reason_message = ' '.join(moderator_message.text.strip().split()[1:])
    else:
        reason_message = ' '.join(moderator_message.text.strip().split()[2:])

    print('Причина мьюта:', reason_message)

    mute_data = {
        'chat_id': moderator_message.chat.id,
        'user_id': user_id,
        'message_id': 00000,  # данное значение неактуально
        'moderator_message': reason_message,
        'admin_username': moderator_message.from_user.username
    }

    await add_mute(mute_data)

    success_message = await moderator_message.answer(
        'Пользователь попал в мьют.'
    )

    await bot.send_message(chat_id=-1002065542994,
                           text=f'Мьют {username},\nuser id: {user_id},\n'
                                f'Подробнее: <a href="t.me/testing_projects_42_bot?show_user=@{username}">'
                                f'<b>/{username}</b></a>\n',
                           parse_mode='HTML'
                           )

    try:
        await bot.delete_message(
            chat_id=moderator_message.chat.id,
            message_id=moderator_message.reply_to_message.message_id
        )
        print('Сообщение с нарушением удалено')
    except Exception as e:
        print('Сообщение с нарушением не удалено, ошибка:', e)

    await delete_message(moderator_message)
    await delete_message(success_message, 1)
