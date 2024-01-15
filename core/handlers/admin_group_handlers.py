from aiogram import Router, Bot, types
from aiogram.filters import Command

from core.database_functions.db_functions import add_lives
from core.filters.admin_filter import AdminFilter
from core.models.data_models import UserData
from core.services.mute import mute
from core.utils.delete_message_with_delay import delete_message
from core.utils.text_checks import checks

admin_group_router = Router()
admin_group_router.message.filter(AdminFilter())


@admin_group_router.message(Command(commands='mute'))
async def mute_handler(moderator_message: types.Message, bot: Bot, session):
    permission = await checks(moderator_message, bot, session)
    if permission[0] is False:
        answer_message = await moderator_message.reply(permission[1])
        await delete_message(answer_message, 2)
        await delete_message(moderator_message)
        return

    if permission[0] is True:
        user_id = permission[1]

    else:
        print('Ошибка выполнения checks')
        return

    data = UserData()
    data.parse_message(moderator_message, user_id if not moderator_message.reply_to_message else None)

    success = await mute(data=data, bot=bot, session=session)
    if not success:
        msg = await moderator_message.answer('Мьют не прошел, отчет об ошибке отправлен разработчику')
        await delete_message(msg, 1)
        await delete_message(moderator_message)
        return

    success_message = await moderator_message.answer(
        f'Пользователь {data.username} попал в мьют.'
    )
    try:
        await bot.delete_message(
            chat_id=moderator_message.chat.id,
            message_id=moderator_message.reply_to_message.message_id
        )
    except Exception as e:
        print('Сообщение с нарушением не удалено, ошибка:', e)

    await delete_message(moderator_message)
    await delete_message(success_message, 1)


@admin_group_router.message(Command('add_unblocks'))
async def add_unblocks_handler(message: types.Message, session):
    user_id = message.reply_to_message.from_user.id
    lives = int(message.text[14:]) if len(str(message.text)) >= 15 else 1
    await add_lives(user_id, session, lives)
    await message.delete()
