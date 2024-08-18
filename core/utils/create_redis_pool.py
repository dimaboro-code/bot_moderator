from redis.asyncio import Redis
from core.config_vars import ConfigVars


def get_conn():
    return Redis.from_url(ConfigVars.REDIS_URL)
