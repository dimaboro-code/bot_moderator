from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker

from .config_vars import ConfigVars

bot = Bot(token=ConfigVars.TOKEN)
dp = Dispatcher()

engine: AsyncEngine = create_async_engine(
    ConfigVars.DATABASE_URL, echo=False, connect_args={"ssl": 'prefer'}
)
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
