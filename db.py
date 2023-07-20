from databases import Database
from datetime import datetime, timedelta


database = Database('postgresql://postgres:2026523@localhost:5432/postgres')


# database functions
"""
Table
Users - user_id, is_muted, user_blocks
Mutes - message_id, chat_id, admin_username (switch to id), moderator_message, date_of_mute
"""


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
                           f'moderator_message, admin_username, date_of_mute) '  # admin un switch to admin_id
                           f'VALUES (:user_id, :message_id, :chat_id, '
                           f':moderator_message, :admin_username, NOW())',
                           values=mute_data)
    user_id = mute_data['user_id']
    change_mute = f'UPDATE users SET is_muted = TRUE WHERE user_id = :user_id'
    values = {'user_id': user_id}
    await database.execute(query=change_mute, values=values)


# Говнокод. Переделать.
async def add_lives(user_id, lives: int = 1):
    lives_in_db = await database.fetch_one(
        f'SELECT user_blocks FROM users WHERE user_id = :user_id',
        values={'user_id': user_id}
    )
    lives = int(lives_in_db[0]) + lives
    await database.execute(
        f'UPDATE users '
        f'SET user_blocks=:lifes '
        f'WHERE user_id=:user_id',
        values={'lifes': lives, 'user_id': user_id}
    )


async def get_user(user_id):  # переделать в get_user и get_mutes
    # из юзердаты количество жизней
    get_user_data = f'SELECT * FROM users WHERE user_id = :user_id'
    user_data = await database.fetch_one(
        query=get_user_data,
        values={'user_id': user_id}
    )
    return user_data


async def get_last_mute(user_id):
    # из мьютов мне нужен айди чата
    query = (f'SELECT * FROM mutes WHERE user_id = :user_id AND id = ('
             f'SELECT MAX (id) FROM mutes WHERE user_id = :user_id)')
    last_mute = await database.fetch_one(
        query=query,
        values={'user_id': user_id}
    )
    return last_mute


async def db_unmute(user_id):
    # функция меняет флаг измьютед на фолс
    change_mute = f'UPDATE users SET is_muted = FALSE WHERE user_id = :user_id'
    values = {'user_id': user_id}
    await database.execute(query=change_mute, values=values)
    lives = await database.fetch_one(f'SELECT user_blocks FROM users WHERE user_id = :user_id',
                                     values={'user_id': user_id})
    lives = int(lives[0]) - 1
    await database.execute(f'UPDATE users SET user_blocks = :user_blocks '
                           f'WHERE user_id = :user_id',
                           values={'user_blocks': lives, 'user_id': user_id})


async def delete_row(user_id):
    delete_user = f'DELETE FROM users ' \
                  f'WHERE user_id = :user_id'

    params = {'user_id': user_id}
    await database.execute(query=delete_user, values=params)


async def add_id(username, user_id):
    # функция создает пару юзернейм - айди, чтобы можно быо мьютить по айди
    query = f'INSERT INTO ids (username, user_id) VALUES (:username, :user_id)'
    params = {'username': username, 'user_id': user_id}
    await database.execute(query=query, values=params)


async def get_id(username):
    query = 'SELECT * FROM ids WHERE username = :username'
    values = {'username': username}
    print(username)
    user_id = await database.fetch_one(query=query, values=values)
    if user_id is not None:
        print(user_id[1])

        return user_id[1]
    else:
        return None


async def delete_old_data():
    print('delete old data')

    # Определите таблицу и поле для удаления данных
    table_name = 'ids'
    field_name = 'created_at'

    # Вычислите временную метку, представляющую время 1 дня назад
    one_day_ago = datetime.now() - timedelta(days=1)

    # Сформируйте SQL-запрос для удаления старых данных
    query = f"DELETE FROM {table_name} WHERE {field_name} < :one_day_ago"

    # Выполните SQL-запрос для удаления старых данных
    await database.execute(query, values={'one_day_ago': one_day_ago})


async def create_table_ids():
    query = f'CREATE TABLE IF NOT EXISTS ids (' \
            f'id SERIAL PRIMARY KEY,' \
            f'user_id NUMERIC NOT NULL,' \
            f'username TEXT,' \
            f'created_at TIMESTAMP DEFAULT NOW())'
    await database.execute(query=query)
    print('таблица создана')
