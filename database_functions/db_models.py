"""
# создаем таблицу users, если её нет
    await connection.execute('
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id NUMERIC NOT NULL UNIQUE,
            user_blocks INTEGER NOT NULL DEFAULT 3,
            is_muted BOOLEAN NOT NULL DEFAULT FALSE
        )
    ')

    # создаем таблицу mutes, если её нет
    await connection execute'
        CREATE TABLE IF NOT EXISTS mutes
            id SERIAL PRIMARY KEY,
            message_id NUMERIC NOT NULL,
            chat_id NUMERIC NOT NULL,
            moderator_message TEXT,
            date_of_mute TIMESTAMP,
            user_id NUMERIC NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            admin_username TEXT NOT NULL

    '
"""
from __future__ import annotations

from typing import List
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import BigInteger, Integer, Boolean, Text, DateTime


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True)
    user_blocks: Mapped[int] = mapped_column(Integer, default=3, nullable=True)
    is_muted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mutes = relationship("Mute", back_populates="user", cascade="all, delete", passive_deletes=True)
    ids = relationship("Id", back_populates="user", cascade="all, delete", passive_deletes=True)


class Mute(Base):
    __tablename__ = 'mutes'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete="CASCADE"))
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    moderator_message: Mapped[str] = mapped_column(Text, nullable=False)
    admin_username: Mapped[str] = mapped_column(Text, nullable=False)
    date_of_mute: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="mutes", cascade='delete')


class Id(Base):
    __tablename__ = 'ids'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete="CASCADE"), unique=True)
    username: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="ids", cascade='delete')

    # async with async_session() as session:
    #     async with session.begin():
    #         session.add_all([
    #             User(user_id=2026523)
    #         ])
    #         session.commit()
    #         session.add_all([
    #             Mute(user_id=2026523, message_id=2, chat_id=4, moderator_message='fff')
    #         ])
    #     stmt = select(User).options(selectinload(User.mutes))
    #     result = await session.execute(stmt)
    #     for i in result.scalars():
    #         print('Юзер айди:', i.user_id)
    #         for mute in i.mutes:
    #             print('Сообщения:', mute.moderator_message)
