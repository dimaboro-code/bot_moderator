import logging
from datetime import datetime, timedelta
import typing

from sqlalchemy import Result, func, and_
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert

from core.database_functions.db_models import User, Mute, Id, Base, DBChat
from core.config import async_session, engine



async def add_user(user_id: int, session = async_session):
    async with session() as session:
        try:
            async with session.begin():
                stmt_user = insert(User).values(user_id=user_id)
                stmt_user = stmt_user.on_conflict_do_nothing(index_elements=['user_id'])
                await session.execute(stmt_user)
            await session.commit()
            print('БД, адд юзер, тз закрыта')
            return True
        except Exception as e:
            await session.rollback()
            print(f'user id {user_id} не добавлен, ошибка:{e}')
            return False


async def add_mute(mute_data, session = async_session):
    user = await get_user(mute_data['user_id'])
    if user is None:
        await add_user(mute_data['user_id'])
    async with session() as session:
        try:
            if session.in_transaction():
                print('хуйня')
                await session.commit()
            async with session.begin():
                # Добавление записи в таблицу Mute
                mute = Mute(
                    user_id=mute_data['user_id'],
                    chat_id=mute_data['chat_id'],
                    moderator_message=mute_data['moderator_message'],
                    admin_username=mute_data['admin_username'],
                    date_of_mute=func.now()
                )
                session.add(mute)
                print('БД, адд мьют, добавление мьюта')

                # Обновление статуса is_muted в таблице User
                query = update(User).where(User.user_id == mute_data['user_id']).values(is_muted=True)
                await session.execute(query)
                print('БД, адд мьют, смена флага')

            await session.commit()  # Фиксация всех изменений в рамках транзакции
            print('Транзакция успешно завершена')
            return True
        except Exception as e:
            await session.rollback()  # Откат изменений при возникновении ошибки
            logging.error('Ошибка при выполнении транзакции добавления мьюта: %s', e)
            return False


async def add_lives(user_id: int, session = async_session, lives: int = 1, *args):
    async with session() as session:
        try:
            # Получаем текущее количество жизней из базы данных
            query = select(User.user_blocks).where(user_id == User.user_id)
            result = await session.execute(query)
            user_blocks = result.scalar()
            if user_blocks < 0:
                print(f'Чет хрень, разблоков меньше нуля, пользователь {user_id}')
                lives = 0
                await session.execute(
                    update(User).where(user_id == User.user_id).values(user_blocks=lives)
                )
                await session.commit()
                return

            # Увеличиваем количество жизней на указанное значение
            new_lives = user_blocks + lives
            print('БД, адд лайвс, новые жизни', new_lives)
            query = update(User).where(user_id == User.user_id).values(user_blocks=new_lives)
            await session.execute(
                query
            )
            await session.commit()
        except Exception as e:
            print('Не удалось добавить жизни, ошибка', e)
            return False


async def delete_lives(user_id: int, session=async_session, deaths: int = 1, *args):
    async with session() as session:
        try:
            # Получаем текущее количество жизней из базы данных
            result = await session.execute(
                select(User.user_blocks).where(user_id == User.user_id)
            )
            user_blocks = result.scalar()
            print("БД, дэлит лайвс, жизни", user_blocks)

            if user_blocks == 0:
                print(f'Пользователь {user_id} не имеет разблоков, нельзя уменьшить')
                return

            if user_blocks < 0:
                print(f'Чет хрень, разблоков меньше нуля, пользователь {user_id}')
                lives = 0
                await session.execute(
                    update(User).where(user_id == User.user_id).values(user_blocks=lives)
                )
                await session.commit()
                return

            # Уменьшаем количество жизней на указанное значение
            new_lives = max(user_blocks - deaths, 0)
            print("БД, дэлит лайвс, новые жизни", new_lives)
            await session.execute(
                update(User).where(user_id == User.user_id).values(user_blocks=new_lives)
            )
            await session.commit()
        except Exception as e:
            print('Делит лайвс, что-то пошло не так, ошибка:', e)


async def delete_all_lives(user_id: int, session = async_session, *args):
    async with session() as session:
        try:
            # Получаем текущее количество жизней из базы данных
            result = await session.execute(
                select(User.user_blocks).where(user_id == User.user_id)
            )
            user_blocks = result.scalar()
            print('БД, удалить все жизни', user_blocks)
            await delete_lives(user_id, deaths=user_blocks)
        except Exception as e:
            print('Удалить все жизни, что-то пошло не так, ошибка: ', e)


async def get_user(user_id: int, session = async_session):
    async with session() as session:
    # Получаем данные пользователя из базы данных
        try:
            result: Result = await session.execute(
                select(User).where(user_id == User.user_id)
            )
            user: User = result.scalar()
            user_data = {
                'user_id': int(user.user_id),
                'user_blocks': user.user_blocks,
                'is_muted': user.is_muted
            }
            await session.commit()
            return user_data
        except Exception as e:
            print('Юзер не найден, ошибка', e)


async def get_last_mute(user_id: int, session = async_session) -> typing.Dict[typing.AnyStr, typing.Any]:
    async with session() as session:
        subquery = select(func.max(Mute.id)).where(user_id == Mute.user_id).scalar_subquery()
        query = select(Mute).filter(user_id == Mute.user_id, Mute.id == subquery)
        try:
            result: Result = await session.execute(query)
            mute: Mute = result.scalar()
            if mute is None:
                return None
            last_mute = {
                'id': mute.id,
                'user_id': int(mute.user_id),
                'chat_id': int(mute.chat_id),
                'moderator_message': mute.moderator_message,
                'admin_username': mute.admin_username,
                'date_of_mute': mute.date_of_mute
            }
            print('БД, Последний мьют', last_mute)
            await session.commit()
            return last_mute
        except Exception as e:
            print('Поиск последнего мьюта сломан, ошибка:', e)


async def get_all_mutes(user_id: int, session = async_session) -> typing.Dict[typing.AnyStr, typing.Any]:
    async with session() as session:
        query = select(Mute).where(user_id == Mute.user_id)
        try:
            result: Result = await session.execute(query)
            mutes = result.scalars().all()
            mutes_list = []
            await session.commit()
            if len(mutes) == 0:
                return
            for mute in mutes:
                mute_dict = {
                    'id': mute.id,
                    'user_id': int(mute.user_id),
                    'chat_id': int(mute.chat_id),
                    'moderator_message': mute.moderator_message,
                    'admin_username': mute.admin_username,
                    'date_of_mute': mute.date_of_mute
                }
                mutes_list.append(mute_dict)
            print('БД, все мьюты', mutes_list)
            return mutes_list
        except Exception as e:
            print('Поиск всех мьютов сломан, ошибка:', e)


async def db_unmute(user_id: int, session = async_session):
    async with session() as session:
        stmt = update(User).where(user_id == User.user_id
                                  ).values(is_muted=False, user_blocks=User.user_blocks - 1
                                           ).returning(User.user_blocks)
        try:
            result = await session.execute(stmt)
            updated_user_blocks = result.scalar()
            if updated_user_blocks is None:
                print(f"Пользователь с ID {user_id} не найден.")
            await session.commit()
            return True
        except Exception as e:
            print('БД, не прошел разблок, ошибка', e)
            return False


async def delete_user(user_id: int, session = async_session):
    async with session() as session:
        # Находим пользователя по user_id и удаляем его
        query = select(User).where(user_id == User.user_id)
        try:
            result: Result = await session.execute(query)
            user: User = result.scalar()
            if user:
                await session.execute(
                    delete(User).where(user_id == User.user_id)
                )
                print(f"Пользователь с ID {user_id} удален.")
            else:
                print(f"Пользователь с ID {user_id} не найден.")
            await session.commit()
        except Exception as e:
            print('Не удалось удалить пользователя, сломано: ', e)


async def add_id(username: str, user_id: int, session = async_session):
    async with session() as session:
        try:
            async with session.begin():
                stmt_id = insert(Id).values(user_id=user_id, username=username)
                stmt_id = stmt_id.on_conflict_do_update(
                    index_elements=['user_id'],
                    set_=dict(created_at=func.NOW())
                )
                await session.execute(stmt_id)

            await session.commit()
            return True

        except Exception as e:
            await session.rollback()
            print(f"Произошла ошибка при добавлении айди: {str(e)}")
            return False


async def get_list_of_id(username: str, session = async_session):
    async with session() as session:
        try:
            result: Result = await session.execute(
                select(Id).where(username == Id.username)
            )
            user_id: list[Id] | None = result.scalars().all()
            print('БД, Гет айди, юзер айди:', user_id[0].user_id if user_id is not None else None)
            await session.commit()
            return [] if user_id is None else user_id

        except Exception as e:
            print('гет айди, Ошибка: ', str(e))


async def get_username(user_id: int, session=async_session):
    async with session() as session:
        try:
            result: Result = await session.execute(
                select(Id.username).where(user_id == Id.user_id)
            )
            username = result.scalar()
            print('БД, Гет юзернейм:', username)
            await session.commit()
            return username

        except Exception as e:
            print('гет юзернейм, Ошибка: ', str(e))


async def db_load_chats(chats_for_db, session=async_session):
    async with session() as session:
        for chat in chats_for_db:
            db_chat = DBChat(
                chat_id=chat.id,
                title=chat.title,
                username=chat.username
            )
            session.add(db_chat)
        await session.commit()
    return True


async def db_update_strict_chats(strict_chats, remove=False, session=async_session):
    async with session() as session:
        for chat_id in strict_chats:
            query = update(DBChat).where(DBChat.chat_id == chat_id).values(strict_mode=not remove)
            await session.execute(query)
            await session.commit()
    return True


async def db_get_strict_chats(session=async_session):
    async with session() as session:
        query = select(DBChat.chat_id).where(DBChat.strict_mode == True)
        result = await session.execute(query)
        strict_chats = result.scalars().all()
        print(strict_chats)
        return strict_chats


async def delete_old_data(session_maker=async_session, days: int = 15, user_id: int = None):
    try:
        async with session_maker() as session:
            days_ago = datetime.now() - timedelta(days=days)

            conditions = (Id.created_at < days_ago)
            if user_id is not None:
                conditions = and_(conditions, Id.user_id == user_id)

            delete_query = delete(Id).where(conditions)

            await session.execute(delete_query)
            await session.commit()
            print('Old data deleted successfully')
    except Exception as e:
        print(f"Произошла ошибка при удалении старых данных: {str(e)}")


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
