from core.config import bot


async def restrict(user_id, chat_id, permissions):
    # mute action
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        # permissions = default parameter name
        permissions=permissions,

        # mute time, if < 30 = forever
        until_date=10
    )
    