from datetime import datetime, timedelta

from aiogram import Router, Bot, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from redis_om import Migrator

from core import ConfigVars
from core.database_functions.db_functions import add_lives, add_mute
from core.database_functions.redis1 import RedisUser
from core.filters.admin_filter import AdminFilter
from core.models.data_models import UserData, BanSteps
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
async def ban_name_handler(message: types.Message, bot: Bot, state: FSMContext):
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
async def ban_name_step(message: types.Message, bot: Bot, state: FSMContext, session):
    print('Бан, степ 1')
    text = message.text.strip()
    Migrator().run()
    users_list = RedisUser.find(RedisUser.username == text).all()
    if len(users_list) == 0:
        await state.clear()
        msg = await message.answer('Пользователь не найден. Если желаете продолжить, введите команду '
                                   '/ban команду заново')
        await delete_message(msg, 2)
        await delete_message(message, 15)
    elif len(users_list) > 1:
        await state.set_state(BanSteps.time_of_message)
        await state.set_data({'users': users_list})
        msg = await message.answer('Найдено несколько пользователей. Чтобы определить, кого банить, напишите'
                                   ', пожалуйста, время последнего сообщения в формате ЧЧ:ММ')
        await delete_message(msg, 2)
        await delete_message(message, 5)
    else:
        user = users_list[0]
        print(users_list)
        if isinstance(user, RedisUser):
            await state.clear()
            tg_id = user.tg_id
            await ban_name(message=message, user_to_ban=tg_id, bot=bot, session=session)
        else:
            await state.clear()
            msg = await message.answer('Неизвестная ошибка, разработчик её уже чинит. Бан не прошел')
            await delete_message(msg, 2)
            await delete_message(message, 15)
            return


@admin_group_router.message(BanSteps.time_of_message)
async def ban_time_step(message: types.Message, bot: Bot, state: FSMContext, session):
    message_text = message.text.strip()
    try:
        target_dt = datetime.strptime(message_text, '%H:%M')
    except ValueError:
        msg = await message.answer(
            'Неверный формат времени. Введите время повторно в формате ЧЧ:ММ или используйте команду /cancel'
        )
        await delete_message(msg, 2)
        await delete_message(message, 5)
        return

    data = await state.get_data()
    users_list = data.get('users')

    if users_list:
        closest_user, min_diff = await calculate_closest_user_time(target_dt.time(), users_list)

        if closest_user:
            precision = abs((datetime.combine(datetime.min, closest_user.time_msg.time()) - target_dt).total_seconds())
            if precision > 300:  # 5 минут = 300 секунд
                msg = await message.answer(
                    'Разница в указанном вами времени с ближайшим пользователем более 5 минут. '
                    'Пожалуйста, проверьте время последнего сообщения еще раз и введите его.'
                )
                await delete_message(msg, 2)
                await delete_message(message, 5)
            else:
                await state.clear()
                tg_id = closest_user.tg_id
                await ban_name(message=message, user_to_ban=tg_id, bot=bot, session=session)
        else:
            msg = await message.answer('Не найдено подходящее время среди пользователей.')
            await delete_message(msg, 2)
            await delete_message(message, 5)
    else:
        await state.clear()
        msg = await message.answer('Неизвестная ошибка, разработчик её уже чинит. Бан не прошел')
        await delete_message(msg, 2)
        await delete_message(message, 15)


async def ban_name(message: types.Message, user_to_ban: int, bot: Bot, session):

    for chat in ConfigVars.CHATS:
        success = await bot.ban_chat_member(chat_id=chat, user_id=user_to_ban, until_date=10, revoke_messages=True)
        if not success:
            with open("ban.log", "a") as f:
                f.write(f'Бан не прошел. Пользователь {user_to_ban}, чат {chat}\n')
    success_message = await message.answer(
        f'Пользователь попал в бан. Отменить данное действие возможно только вручную '
    )
    await add_mute(mute_data={
            'user_id': user_to_ban,
            'chat_id': ConfigVars.CHATS[0],
            'moderator_message': 'Пользователь забанен',
            'admin_username':message.from_user.username
        }, session=session)
    try:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.message_id
        )
    except Exception as e:
        print('Сообщение с нарушением не удалено, ошибка:', e)

    await delete_message(message)
    await delete_message(success_message, 1)


async def calculate_closest_user_time(target_time, users_list):
    min_diff = timedelta.max
    closest_user = None

    target_dt = datetime.combine(datetime.min, target_time)

    for user in users_list:
        user_time = user.time_msg.time()
        current_dt = datetime.combine(datetime.min, user_time)
        diff = abs(target_dt - current_dt)
        if diff < min_diff:
            min_diff = diff
            closest_user = user
    return closest_user, min_diff
