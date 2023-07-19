import asyncio

import sqlalchemy
from sqlalchemy import Column, Integer, Numeric, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.__init__ import dialect
from databases import Database



# async def create_tables(connection):
#     # создаем таблицу users, если её нет
#     await connection.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id SERIAL PRIMARY KEY,
#             user_id NUMERIC NOT NULL UNIQUE,
#             user_blocks INTEGER NOT NULL DEFAULT 3,
#             is_muted BOOLEAN NOT NULL DEFAULT FALSE
#         )
#     ''')
#
#     # создаем таблицу mutes, если её нет
#     await connection.execute('''
#         CREATE TABLE IF NOT EXISTS mutes (
#             id SERIAL PRIMARY KEY,
#             message_id NUMERIC NOT NULL,
#             chat_id NUMERIC NOT NULL,
#             moderator_message TEXT,
#             date_of_mute TIMESTAMP,
#             user_id NUMERIC NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
#             admin_username TEXT NOT NULL
#         )
#     ''')

Base = declarative_base()
metadata = sqlalchemy.MetaData()
dialect = dialect()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Numeric, nullable=False, unique=True)
    user_blocks = Column(Integer, nullable=False, default=3)
    is_muted = Column(Boolean, nullable=False, default=False)
    metadata = metadata


class Mute(Base):
    __tablename__ = 'mutes'

    id = Column(Integer, primary_key=True)
    message_id = Column(Numeric, nullable=False)
    chat_id = Column(Numeric, nullable=False)
    moderator_message = Column(Text)
    date_of_mute = Column(TIMESTAMP)
    user_id = Column(Numeric, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    admin_username = Column(Text, nullable=False)
    metadata = metadata

    user = relationship('User')


async def main():
    database = Database('postgresql+asyncpg://postgres:2026523@localhost:5432/postgres')
    await database.connect()
    # async with database.connection() as connection:
    #     await create_tables(connection)
    for table in metadata.tables.values():
        # Set `if_not_exists=False` if you want the query to throw an
        # exception when the table already exists
        schema = sqlalchemy.schema.CreateTable(table, if_not_exists=True)
        query = str(schema.compile(dialect=dialect))
        await database.execute(query=query)

    table = metadata.tables['users']
    # table.


    await database.disconnect()
asyncio.run(main())
