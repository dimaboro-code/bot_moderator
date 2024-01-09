from typing import List
from aiogram import Bot, types
from core.config_vars import ConfigVars
from core.utils.send_report import send_report_to_group


async def restrict(user_id: int, chat_id: int, bot: Bot, chats: List[int] = ConfigVars.CHATS,
                   permissions: types.ChatPermissions = ConfigVars.MUTE_SETTINGS
                   ) -> bool:
    report = {}
    exeps = {}
    for chat_id in chats:
        try:
            success = await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=permissions,
                # mute time, if < 30 = forever
                until_date=10
            )
            report[chat_id] = success
        except Exception as e:
            success = False
            report[chat_id] = success
            exeps[chat_id] = e
            continue

    # если минимум в одном чате мьют не прошел
    if False in report.values():
        # если ни в одном не прошел
        if True not in report.values():
            return False
        problem_list = [f'Не прошел мьют в чате{chat_id}, ошибка: {e}' for chat_id, e in exeps.items()]
        problem = '\n'.join(problem_list)
        await send_report_to_group(user_id=user_id, user_username='no matter', chat_id=chat_id, chat_username='None',
                                   problem=problem)  # TODO переделать в модель для данных
    return True  # TODO переделать в модель для данных
