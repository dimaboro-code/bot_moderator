from redis.asyncio import Redis
from core.config import ConfigVars
from urllib.parse import urlparse


def get_conn():
    url = urlparse(ConfigVars.REDIS_URL)
    r = Redis(host=url.hostname, port=url.port, password=url.password, ssl=(url.scheme == "rediss"), ssl_cert_reqs=None)
    return r
