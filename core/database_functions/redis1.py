from datetime import datetime
from typing import Optional

from redis_om import HashModel, Field


class RedisUser(HashModel):
    tg_id: int = Field(index=True)
    username: str = Field(index=True)
    time_msg: Optional[datetime] = Field(index=True)
