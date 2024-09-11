from aiogram import Router, Bot, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from core import ConfigVars
from core.database_functions.db_functions import add_lives, db_update_strict_chats
from core.filters.admin_filter import AdminFilter
from core.models.data_models import UserData, BanSteps
from core.services.mute import mute
from core.utils.delete_message_with_delay import delete_message
from core.utils.text_checks import checks, get_id_from_text, get_id_from_entities

admin_group_router = Router()
admin_group_router.message.filter(AdminFilter())


@admin_group_router.message(Command('strict_mode_on'))
async def strict_mode_on(message: types.Message, strict_chats: list):
    if message.chat.id in strict_chats:
        msg = await message.answer('В чате уже включен строгий режим')
    else:
        strict_chats.append(message.chat.id)
        await db_update_strict_chats(strict_chats)
        msg = await message.answer('Успешно')
    await delete_message(msg, 2)
    await message.delete()


@admin_group_router.message(Command('strict_mode_off'))
async def strict_mode_off(message: types.Message, strict_chats: list):
    if message.chat.id in strict_chats:
        await db_update_strict_chats(strict_chats, remove=True)
        strict_chats.remove(message.chat.id)
        msg = await message.answer('Успешно')
    else:
        msg = await message.answer('Строгий режим отключен')
    await delete_message(msg, 2)
    await message.delete()


@admin_group_router.message(Command(commands='mute'))
async def mute_handler(moderator_message: types.Message, bot: Bot):
    permission = await checks(moderator_message, bot)
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

    success = await mute(data=data, bot=bot)
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
async def add_unblocks_handler(message: types.Message):
    user_id = message.reply_to_message.from_user.id
    lives = int(message.text[14:]) if len(str(message.text)) >= 15 else 1
    await add_lives(user_id, lives)
    await message.delete()


@admin_group_router.message(Command(commands='ban'), F.reply_to_message)
async def ban_reply_handler(moderator_message: types.Message, bot: Bot):
    user_to_ban = moderator_message.reply_to_message.from_user.id
    for chat in ConfigVars.CHATS:
        success = await bot.ban_chat_member(chat_id=chat, user_id=user_to_ban, until_date=10, revoke_messages=True)
        if not success:
            with open("ban.log", "a") as f:
                f.write(f'Бан не прошел. Пользователь {user_to_ban}, чат {chat}\n')
                await bot.send_message(chat_id=ConfigVars.LOG_CHAT, text=f'Бан не прошел. Пользователь {user_to_ban}'
                                                                         f', чат {chat}\n')
    success_message = await moderator_message.answer(
        f'Пользователь попал в бан. Отменить данное действие возможно только вручную '
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


@admin_group_router.message(Command(commands='ban'))
async def ban_name_handler(message: types.Message, state: FSMContext, bot: Bot):
    user_id = await get_id_from_text(message.text)
    # Если текст - это юзернейм или айди, то айди найден. Если текст - не айди и не юзернейм, то не найден
    if user_id is None and len(message.text.split()) > 1:
        user_id = await get_id_from_entities(message.entities)
    # Если текст есть, но не содержит айди или юзернейм, ищем его в энтити
    if user_id is not None:
        await ban_name(message=message, user_to_ban=user_id, bot=bot)
        return
    # и если нашли - баним
    # А если не нашли - то сообщаем, что не нашли

    await state.set_state(BanSteps.name)
    msg = await message.answer('Пожалуйста, укажите юзернейм пользователя. Если юзернейм отсутствует, '
                               'укажите имя и фамилию пользователя. Если фамилия также отсутствует,'
                               'укажите только имя.')
    await delete_message(msg, 15)
    await message.delete()


@admin_group_router.message(Command(commands='cancel'))
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    msg = await message.answer('Процедура бана сброшена')
    await delete_message(msg, 3)
    await message.delete()


@admin_group_router.message(BanSteps.name)
async def ban_name_step(message: types.Message, bot: Bot, state: FSMContext):
    """
    Надо переписать, чтобы для безюзернеймовых брать инфу не из базы, а из энтитис
    Args:
        message:
        bot:
        state:

    Returns:

    """
    # гет айди работает только со вторым словом из текста. Поэтому я сделал костыль, чтобы не менять всю функцию
    user_id = await get_id_from_text(f'костыль {message.text}')
    # Если текст - это юзернейм или айди, то айди найден. Если текст - не айди и не юзернейм, то не найден
    if user_id is None:
        user_id = await get_id_from_entities(message.entities)
        if user_id is None:
            await state.clear()
            msg = await message.answer('Пользователь не найден. Если желаете продолжить, введите команду '
                                       '/ban команду заново')
            await delete_message(msg, 2)
            await delete_message(message, 15)
            return
    await state.clear()
    await ban_name(message=message, user_to_ban=user_id, bot=bot)


async def ban_name(message: types.Message, user_to_ban: int, bot: Bot):

    for chat in ConfigVars.CHATS:
        success = await bot.ban_chat_member(chat_id=chat, user_id=user_to_ban, until_date=10, revoke_messages=True)
        if not success:
            with open("ban.log", "a") as f:
                f.write(f'Бан не прошел. Пользователь {user_to_ban}, чат {chat}\n')
    success_message = await message.answer(
        f'Пользователь попал в бан. Отменить данное действие возможно только вручную '
    )
    try:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.message_id
        )
    except Exception as e:
        print('Сообщение с нарушением не удалено, ошибка:', e)

    await delete_message(message)
    await delete_message(success_message, 1)
