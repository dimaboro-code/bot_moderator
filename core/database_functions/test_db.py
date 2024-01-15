"""
для истории - красивый запрос для добавления зависимости unique
DELETE FROM ids
WHERE (id, user_id) NOT IN (
    SELECT id, user_id
    FROM (
        SELECT id, user_id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY id DESC) AS rn
        FROM ids
        WHERE username IS NOT NULL
    ) sub
    WHERE rn = 1
);

ALTER TABLE ids
ADD CONSTRAINT ids_user_id_key UNIQUE (user_id);

"""
from core.database_functions.db_functions import add_user, add_lives, add_mute, get_user, \
    get_last_mute, delete_lives, db_unmute, delete_all_lives, add_id, \
    get_id, delete_old_data, delete_user, engine as eng
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

CONN: AsyncEngine = eng


async def test_simple_db(session: AsyncSession, engine: AsyncEngine = CONN) -> bool:
    test_user_id = 2026523
    try:
        await add_user(user_id=test_user_id, session=session)
        await add_lives(user_id=test_user_id, session=session)
        await add_mute(mute_data={
            'chat_id': 444,
            'user_id': test_user_id,
            'moderator_message': 'fff',
            'admin_username': 'dimaboro'
        }, session=session)
        await get_user(user_id=test_user_id, session=session)
        await get_last_mute(user_id=test_user_id, session=session)
        await delete_lives(user_id=test_user_id, session=session)
        await db_unmute(user_id=test_user_id, session=session)
        await delete_all_lives(user_id=test_user_id, session=session)
        await add_id(user_id=test_user_id, username='dds', session=session)
        await get_id(username='dds', session=session)
        await delete_old_data(days=0, user_id=test_user_id)
        await delete_user(user_id=test_user_id, session=session)
        print('Тесты бд успешно пройдены')
        await engine.dispose()
        return True
    except Exception as e:
        print('Тесты бд не прошли', e)
        return False


