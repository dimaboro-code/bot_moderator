from databases import Database
from config import DATABASE_URL


database = Database(DATABASE_URL + '?ssl=true')


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
                           f'moderator_message, admin_username, date_of_mute) '
                           f'VALUES (:user_id, :message_id, :chat_id, '
                           f':moderator_message, :admin_username, NOW())',
                           values=mute_data)
    user_id = mute_data['user_id']
    lives = await database.fetch_one(f'SELECT user_blocks FROM users WHERE user_id = :user_id',
                                     values={'user_id': user_id})
    lives = int(lives[0]) - 1
    await database.execute(f'UPDATE users SET user_blocks = :user_blocks, is_muted = TRUE '
                           f'WHERE user_id = :user_id',
                           values={'user_blocks': lives, 'user_id': user_id})


async def get_user_data(user_id):
    # из мьютов мне нужен айди чата
    # из юзердаты количество жизней
    get_last_mute = (f'SELECT * FROM mutes WHERE user_id = :user_id AND id = ('
                 f'SELECT MAX (id) FROM mutes WHERE user_id = :user_id)')
    get_user_data = f'SELECT * FROM users WHERE user_id = :user_id'
    last_mute = await database.fetch_one(
        query=get_last_mute,
        values={'user_id': user_id}
    )
    user_data = await database.fetch_one(
        query=get_user_data,
        values={'user_id': user_id}
    )

    return (last_mute, user_data)


async def db_unmute():
    # функция меняет флаг измьютед на фолс
    change_mute = f'UPDATE users SET is_muted = FALSE'
    await database.execute(query=change_mute)


async def delete_row(user_id):
    delete_user = f'DELETE FROM users ' \
                  f'WHERE user_id = :user_id'

    params = {'user_id': user_id}
    await database.execute(query=delete_user, values=params)
