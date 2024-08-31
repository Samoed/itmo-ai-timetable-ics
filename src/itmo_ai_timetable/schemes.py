from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Pair(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    pair_type: str | None = None
    link: str | None = None


class ClassStatus(Enum):
    need_to_add = "need_to_add"
    need_to_delete = "need_to_delete"
    deleted = "deleted"
    need_to_update = "need_to_update"
    synced = "synced"
