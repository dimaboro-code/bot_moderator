import logging
from datetime import datetime, timedelta

from sqlalchemy import Result, func, and_
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.database_functions.db_models import User, Mute, Id, Base
from core.config import async_session, engine

session = async_session


async def add_user(user_id: int, session: AsyncSession = session):
    try:
        async with session.begin():
            stmt_user = insert(User).values(user_id=user_id)
            stmt_user = stmt_user.on_conflict_do_nothing(index_elements=['user_id'])
            await session.execute(stmt_user)
        await session.commit()
        print('БД, адд юзер')
        return True
    except Exception as e:
        print(f'user id {user_id} не добавлен, ошибка:{e}')
        return False


async def delete_row(user_id: int):
    try:
        async with async_session() as session:
            session: AsyncSession
            stmt = delete(User).where(user_id == User.user_id)
            await session.execute(stmt)
            await session.commit()
            print('БД, делит роу, без ретерна')
    except ExceptionGroup as e:
        print(f'Запись не удалена, ошибка: {e}')


async def add_mute(mute_data):
    async with async_session() as session:
        try:
            async with session.begin():
                # Добавление записи в таблицу Mute
                mute = Mute(
                    user_id=mute_data['user_id'],
                    chat_id=mute_data['chat_id'],
                    moderator_message=mute_data['moderator_message'],
                    admin_username=mute_data['admin_username'],
                    message_id=1
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
            logging.error('Ошибка при выполнении транзакции: %s', e)
            return False


async def add_lives(user_id: int, lives: int = 1):
    async with async_session() as session:
        # Получаем текущее количество жизней из базы данных
        result = await session.execute(
            select(User.user_blocks).where(user_id == User.user_id)
        )
        user_blocks = result.scalar()
        print('БД, адд лайвс, текущее колво жизней', user_blocks)

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
        await session.execute(
            update(User).where(user_id == User.user_id).values(user_blocks=new_lives)
        )
        await session.commit()


async def delete_lives(user_id: int, deaths: int = 1):
    async with async_session() as session:
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


async def delete_all_lives(user_id: int):
    async with async_session() as session:
        # Получаем текущее количество жизней из базы данных
        result = await session.execute(
            select(User.user_blocks).where(user_id == User.user_id)
        )
        user_blocks = result.scalar()
        print('БД, удалить все жизни', user_blocks)
        await delete_lives(user_id, deaths=user_blocks)


async def get_user(user_id: int):
    async with async_session() as session:
        session: AsyncSession
        # Получаем данные пользователя из базы данных
        result: Result = await session.execute(
            select(User).where(user_id == User.user_id)
        )
        user: User = result.scalar()
        user_data = {
            'user_id': user.user_id,
            'user_blocks': user.user_blocks,
            'is_muted': user.is_muted
        }
        print('БД, гет юзер', user_data)
        return user_data


async def get_last_mute(user_id: int):
    async with async_session() as session:
        session: AsyncSession
        subquery = select(func.max(Mute.id)).where(user_id == Mute.user_id).scalar_subquery()

        query = select(Mute).filter(user_id == Mute.user_id, Mute.id == subquery)

        result: Result = await session.execute(query)
        mute: Mute | None = result.scalar()
        if mute is None:
            return mute

        last_mute = {
            'id': mute.id,
            'user_id': mute.user_id,
            'message_id': mute.message_id,
            'chat_id': mute.chat_id,
            'moderator_message': mute.moderator_message,
            'admin_username': mute.admin_username,
            'date_of_mute': mute.date_of_mute
        }
        print('БД, Последний мьют', last_mute)
        return last_mute


async def db_unmute(user_id: int):
    async with async_session() as session:
        session: AsyncSession
        stmt = update(User).where(user_id == User.user_id
                                  ).values(is_muted=False, user_blocks=User.user_blocks - 1
                                           ).returning(User.user_blocks)
        result = await session.execute(stmt)
        updated_user_blocks = result.scalar()
        print('БД, анмьют')

        if updated_user_blocks is not None:
            print(f"Новое значение user_blocks: {updated_user_blocks}")
        else:
            print(f"Пользователь с ID {user_id} не найден.")
        await session.commit()


async def delete_user(user_id: int):
    async with async_session() as session:
        session: AsyncSession

        # Находим пользователя по user_id и удаляем его
        result: Result = await session.execute(
            select(User).where(user_id == User.user_id)
        )
        user: User = result.scalar()
        if user:
            await session.execute(
                delete(User).where(user_id == User.user_id)
            )
            await session.commit()
            print(f"Пользователь с ID {user_id} удален.")
        else:
            print(f"Пользователь с ID {user_id} не найден.")


async def add_id(username: str, user_id: int, session: AsyncSession = session):
    print('БД, адд айди')
    try:
        async with session.begin():
            stmt_id = insert(Id).values(user_id=user_id, username=username)
            stmt_id = stmt_id.on_conflict_do_update(
                index_elements=['user_id'],
                set_=dict(created_at=func.NOW())
            )
            await session.execute(stmt_id)

        await session.commit()
        print('ID успешно добавлен в базу или обновлен')
        return True

    except Exception as e:
        print(f"Произошла ошибка при добавлении айди: {str(e)}")
        return False


async def get_id(username: str, session: AsyncSession = session):
    try:
        result: Result = await session.execute(
            select(Id.user_id).where(username == Id.username)
        )
        user_id = result.scalar()
        print('БД, Гет айди, юзер айди:', user_id)
        return user_id

    except Exception as e:
        print('Ошибка: ', str(e))


async def delete_old_data(days: int = 5, user_id: int = None):
    async with async_session() as session:
        session: AsyncSession
        try:
            print('Deleting old data, user id:', user_id)

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


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
