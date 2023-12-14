import asyncio
import logging
from datetime import datetime, timedelta

from db_models import User, Mute, Id, Base
from sqlalchemy import select, delete, update, insert
from sqlalchemy import Result, func
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.exc import SQLAlchemyError

engine: AsyncEngine = create_async_engine(
    'postgresql+asyncpg://postgres:2026523@localhost:5432/postgres', echo=False
)
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
logging.basicConfig(level=logging.WARNING)


async def in_database(user_id=2026523):
    async with async_session() as session:
        stmt = select(User).where(User.user_id == user_id)
        result: Result = await session.execute(stmt)
        try:
            user: User = result.scalar()
            print(user.user_id)
        except Exception as e:
            logging.error('Нельзя принтануть юзера, %s', e)
    return bool(user)


async def add_user(user_id=2026523):
    try:
        async with async_session() as session:
            user = User(user_id=user_id)
            session.add(user)
            await session.commit()
    except Exception as e:
        print(f'user id {user_id} не добавлен, ошибка:{e}')


async def delete_row(user_id=2026523):
    try:
        async with async_session() as session:
            session: AsyncSession
            stmt = delete(User).where(User.user_id == user_id)
            await session.execute(stmt)
    except ExceptionGroup as e:
        print(f'Запись не удалена, ошибка: {e}')


async def add_mute(mute_data):
    try:

        async with async_session() as session:
            session: AsyncSession
            async with session.begin():
                mute = Mute(
                    user_id=mute_data['user_id'],
                    chat_id=mute_data['chat_id'],
                    moderator_message=mute_data['moderator_message'],
                    admin_username=mute_data['admin_username'],
                    message_id=1
                )
                session.add(mute)
            # await session.commit()

        # Обновление статуса is_muted в отдельной сессии
        async with async_session() as update_session:
            query = update(User).where(User.user_id == mute.user_id).values(is_muted=True)
            await update_session.execute(query)
            await update_session.commit()

    except SQLAlchemyError as sql_err:
        logging.error('Ошибка SQLAlchemy при добавлении mute: %s', sql_err)
    except KeyError as key_err:
        logging.error('Отсутствует ключ в данных для mute: %s', key_err)
    except Exception as e:
        logging.error('Ошибка при добавлении mute: %s', e)


async def add_lives(user_id=2026523, lives: int = 1):
    async with async_session() as session:
        # Получаем текущее количество жизней из базы данных
        result = await session.execute(
            select(User.user_blocks).where(User.user_id == user_id)
        )
        user_blocks = result.scalar()

        if user_blocks < 0:
            print(f'Чет хрень, разблоков меньше нуля, пользователь {user_id}')
            lives = 0
            await session.execute(
                update(User).where(User.user_id == user_id).values(user_blocks=lives)
            )
            await session.commit()
            return

        # Увеличиваем количество жизней на указанное значение
        new_lives = user_blocks + lives
        print(new_lives)
        await session.execute(
            update(User).where(User.user_id == user_id).values(user_blocks=new_lives)
        )
        await session.commit()


async def delete_lives(user_id=2026523, deaths: int = 1):
    async with async_session() as session:
        # Получаем текущее количество жизней из базы данных
        result = await session.execute(
            select(User.user_blocks).where(User.user_id == user_id)
        )
        user_blocks = result.scalar()

        if user_blocks == 0:
            print(f'Пользователь {user_id} не имеет разблоков, нельзя уменьшить')
            return

        if user_blocks < 0:
            print(f'Чет хрень, разблоков меньше нуля, пользователь {user_id}')
            lives = 0
            await session.execute(
                update(User).where(User.user_id == user_id).values(user_blocks=lives)
            )
            await session.commit()
            return

        # Уменьшаем количество жизней на указанное значение
        new_lives = max(user_blocks - deaths, 0)
        print(new_lives)
        await session.execute(
            update(User).where(User.user_id == user_id).values(user_blocks=new_lives)
        )
        await session.commit()


async def delete_all_lives(user_id=2026523):
    async with async_session() as session:
        # Получаем текущее количество жизней из базы данных
        result = await session.execute(
            select(User.user_blocks).where(User.user_id == user_id)
        )
        user_blocks = result.scalar()
        print(user_blocks)
        await delete_lives(user_id, deaths=user_blocks)


async def get_user(user_id=2026523):
    async with async_session() as session:
        session: AsyncSession
        # Получаем данные пользователя из базы данных
        result: Result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user: User = result.scalar()
        user_data = {
            'user_id': user.user_id,
            'user_blocks': user.user_blocks,
            'is_muted': user.is_muted
        }
        print(user_data)
        return user_data


async def get_last_mute(user_id=2026523):
    async with async_session() as session:
        session: AsyncSession
        subquery = select(func.max(Mute.id)).where(Mute.user_id == user_id).scalar_subquery()

        query = select(Mute).filter(Mute.user_id == user_id, Mute.id == subquery)

        result: Result = await session.execute(query)
        mute: Mute = result.scalar()

        last_mute = {
            'id': mute.id,
            'user_id': mute.user_id,
            'message_id': mute.message_id,
            'chat_id': mute.chat_id,
            'moderator_message': mute.moderator_message,
            'admin_username': mute.admin_username,
            'date_of_mute': mute.date_of_mute
        }
        print(last_mute)
        return last_mute


async def db_unmute(user_id=2026523):
    async with async_session() as session:
        session: AsyncSession
        await session.execute(
            update(User).where(User.user_id == user_id).values(is_muted=False)
        )

        # Получаем количество блокировок пользователя и уменьшаем на 1
        stmt = update(User).where(User.user_id == user_id).values(user_blocks=User.user_blocks - 1).returning(
            User.user_blocks)
        result = await session.execute(stmt)
        updated_user_blocks = result.scalar()

        if updated_user_blocks is not None:
            print(f"Новое значение user_blocks: {updated_user_blocks}")
        else:
            print(f"Пользователь с ID {user_id} не найден.")
        await session.commit()


async def delete_row(user_id=222):
    async with async_session() as session:
        session: AsyncSession

        # Находим пользователя по user_id и удаляем его
        result: Result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user: User = result.scalar()
        if user:
            await session.execute(
                delete(User).where(User.user_id == user_id)
            )
            await session.commit()
            print(f"Пользователь с ID {user_id} удален.")
        else:
            print(f"Пользователь с ID {user_id} не найден.")


async def add_or_update_id(username='dds', user_id=2026523):
    async with async_session() as session:
        session: AsyncSession
        try:
            # Попытка вставки новой записи
            await session.execute(
                insert(Id).values(username=username, user_id=user_id)
            )
            print('ID успешно добавлен в базу')
            await session.commit()

        except Exception as e:
            print(f"Произошла ошибка при добавлении идентификатора: {str(e)}")

            # Если произошла ошибка вставки, попробовать обновить существующую запись
            try:
                await session.execute(
                    update(Id).where(Id.user_id == user_id).values(created_at=func.NOW())
                )
                print('Обновление прошло успешно')
                await session.commit()

            except Exception as update_error:
                print(f"Произошла ошибка при обновлении идентификатора: {str(update_error)}")


async def check_known_id(user_id=2026523):
    async with async_session() as session:
        try:
            result: Result = await session.execute(
                select(Id.username).where(Id.user_id == user_id)
            )
            username = result.all()
            print(username)
            return username[0][0]

        except Exception as e:
            print(f"Произошла ошибка при получении идентификатора: {str(e)}")


async def get_id(username='dds'):
    async with async_session() as session:
        try:
            result: Result = await session.execute(
                select(Id.user_id).where(Id.username == username)
            )
            user_id = result.all()
            print('Гет айди, юзер айди:', int(user_id[0][0]))
            return user_id

        except Exception as e:
            print('Ошибка: ', str(e))


async def delete_old_data():
    async with async_session() as session:
        session: AsyncSession
        try:
            print('Deleting old data')

            two_days_ago = datetime.now() - timedelta(days=5)

            await session.execute(
                delete(Id).where(Id.created_at < two_days_ago)
            )
            await session.commit()
            print('Old data deleted successfully')
        except Exception as e:
            print(f"Произошла ошибка при удалении старых данных: {str(e)}")



async def main():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(main())
