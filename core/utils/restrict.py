from typing import List
from aiogram import Bot, types
from core.config import ConfigVars
from core.utils.send_report import send_bug_report


async def restrict(user_id: int, chat_id_orig: int, bot: Bot, chats: List[int] = ConfigVars.CHATS,
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

    # если минимум в одном чате мьют не прошел
    if False in report.values():
        problem_list = [f'Не прошел мьют в чате{chat_id}, ошибка: {e}' for chat_id, e in exeps.items()]
        problem = '\n'.join(problem_list)
        await send_bug_report(user_id=user_id, user_username='no matter', chat_id=chat_id_orig, chat_username='None',
                              problem=problem, bot=bot)
        # если ни в одном не прошел
        if True not in report.values():
            return False
    return True
