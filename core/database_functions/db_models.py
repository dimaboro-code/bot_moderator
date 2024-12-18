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

from datetime import datetime

from sqlalchemy import Integer, Boolean, Text, DateTime, Numeric, BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from core import ConfigVars


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Numeric, unique=True, nullable=False)
    user_blocks: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    is_muted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mutes = relationship("Mute", back_populates="user", cascade="all, delete", passive_deletes=True)
    ids = relationship("Id", back_populates="user", cascade="all, delete", passive_deletes=True)


class Mute(Base):
    __tablename__ = 'mutes'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete="CASCADE"))
    chat_id: Mapped[int] = mapped_column(Numeric, nullable=False)
    moderator_message: Mapped[str] = mapped_column(Text)
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


class DBChat(Base):
    __tablename__ = 'chats'
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    username: Mapped[str] = mapped_column(Text, nullable=True)
    strict_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    capcha: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


engine: AsyncEngine = create_async_engine(
    ConfigVars.DATABASE_URL, echo=False, connect_args={"ssl": 'prefer'}
)
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
