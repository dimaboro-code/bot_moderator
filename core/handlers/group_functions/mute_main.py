from aiogram import types

from core.config import bot, CHATS, MUTE_SETTINGS, LOG_CHANNEL

from core.utils.delete_message import delete_message
from core.utils.restrict import restrict
from database_functions.db_functions import *
from core.handlers.group_functions.mute_checks import checks


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

    if permission[0] is True:
        user_id = permission[1]

    else:
        print('Вообще в душе не ебу, что может произойти, чтобы выполнилась эта ветка')
        return

    try:
        bad_user: types.ChatMember = await bot.get_chat_member(moderator_message.chat.id, user_id)
        username = bad_user.user.username
    except Exception as exep:
        username = 'mistake_in_code'
        await bot.send_message(
            chat_id=-1001838011289,
            text=f'mute_main, 42\nНе удалось добыть юзернейм, причина: {exep}'
        )

    for chat_id in CHATS:
        chat: types.Chat = await bot.get_chat(chat_id)
        try:
            await restrict(user_id, chat_id, MUTE_SETTINGS)
            print(chat.username, ': успешно')
        except Exception as e:
            print(chat.username, ': ошибка', e)
            await bot.send_message(
                chat_id=-1001868029361,
                text=f'Юзер: {user_id}\n'
                     f'Юзернейм: @{username}'
                     f'Чат ID: {chat.id}\n'
                     f'Чат: @{chat.username}\n'
                     f'Не прошел мьют, ошибка: {e}'
            )
            continue

    member_actual_state = await bot.get_chat_member(chat_id=moderator_message.chat.id, user_id=user_id)
    if member_actual_state.status != 'restricted' or member_actual_state.can_send_messages:
        ans = await moderator_message.answer('Мьют не прошел, отчет об ошибке отправлен разработчику')
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

    try:
        await bot.send_message(chat_id=LOG_CHANNEL,
                               text=f'Мьют @{username},\nuser id: {user_id},\n'
                                    f'Подробнее: <a href="t.me/slashdbot?start={username}">'
                                    f'<b>{username}</b></a>\n\n'
                                    f'Админ: @{moderator_message.from_user.username}\n'
                                    f'Причина: {reason_message}',
                               parse_mode='HTML'
                               )
    except Exception as exep:
        await bot.send_message(
            chat_id=-1001868029361,
            text=f'Юзер: {user_id}\n'
                 f'Юзернейм: {username}'
                 f'Чат: {chat.username}\n'
                 f'Не прошел отчет о мьюте, ошибка: {exep}'
        )

    success_message = await moderator_message.answer(
        f'Пользователь {username} попал в мьют.'
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
