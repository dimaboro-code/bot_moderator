from databases import Database
from config import DATABASE_URL

database = Database(DATABASE_URL)


# database functions
async def in_database(user_id):
    results = await database.fetch_all(f'SELECT * FROM users '
                                       f'WHERE user_id = :user_id',
                                       values={'user_id': user_id})
    return bool(len(results))


async def add_user(user_id):
    await database.execute(f'INSERT INTO users (user_id, is_muted) '
                           f'VALUES (:user_id, :is_muted)',
                           values={'user_id': user_id,
                                   'is_muted': True})


async def add_mute(mute_data):
    await database.execute(f'INSERT INTO mutes (user_id, message_id, chat_id, '
                           f'moderator_message, admin_username) '
                           f'VALUES (:user_id, :message_id, :chat_id, '
                           f':moderator_message, :admin_username)',
                           values=mute_data)
    user_id = mute_data['user_id']
    lives = await database.fetch_one(f'SELECT user_blocks FROM users WHERE user_id = :user_id',
                                     values={'user_id': user_id})
    lives = int(lives[0]) - 1
    await database.execute(f'UPDATE users SET user_blocks = :user_blocks, is_muted = TRUE '
                           f'WHERE user_id = :user_id',
                           values={'user_blocks': lives, 'user_id': user_id})


async def remove_from_mute(user_id):
    results = await database.fetch_all(
        f'SELECT * FROM mutes WHERE user_id = :user_id AND id = ('
        f'SELECT MAX (id) FROM mutes WHERE user_id = :user_id)',
        values={'user_id': user_id}
    )
    user_data = [next(res.values()) for res in results]
    return [str(x) for x in user_data]

