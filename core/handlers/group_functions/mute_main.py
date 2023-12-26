from aiogram import types, Bot

from core.config import bot as my_bot
from core.database_functions.db_functions import *
from core.handlers.group_functions.mute_checks import checks
from core.utils.delete_message import delete_message
from core.utils.restrict import restrict
from core.utils.send_report import send_report_to_channel, send_report_to_group


async def mute(moderator_message: types.Message, bot: Bot = my_bot):
    """
    Функция для выполнения команды /mute и мьюта пользователя.

    Args:
        bot:
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

    try:  # TODO переписать чтобы только для мьюта по юзернейму
        bad_user: types.ChatMember = await bot.get_chat_member(moderator_message.chat.id, user_id)
        username = bad_user.user.username
    except Exception as problem:
        username = 'mistake_in_code'
        await send_report_to_group(user_id, username, moderator_message.chat.id,
                                   moderator_message.chat.username, problem, bot)

    chats = Config.CHATS
    for chat_id in chats:
        chat: types.Chat = await bot.get_chat(chat_id)
        try:
            await restrict(user_id, chat_id, Config.MUTE_SETTINGS)
            print(chat.username, ': успешно')

        except Exception as e:
            print(chat.username, ': ошибка', e)

            problem = f'Не прошел мьют, ошибка: {e}'
            await send_report_to_group(user_id, username, chat.id, chat.username, problem)

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
        'message_id': 00000,  # данное значение неактуально TODO выпилить нахуй
        'moderator_message': reason_message,
        'admin_username': moderator_message.from_user.username
    }

    await add_mute(mute_data)
    admin = moderator_message.from_user.username
    chat_username: str = moderator_message.chat.username

    try:
        await send_report_to_channel(user_id, username, admin, chat_username, reason_message)
    except Exception as problem:
        await send_report_to_group(user_id, username, moderator_message.chat.id,
                                   chat_username, problem)

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
