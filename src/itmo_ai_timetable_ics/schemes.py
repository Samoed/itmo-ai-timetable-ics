from datetime import datetime

from pydantic import BaseModel


class Pair(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    pair_type: str | None
    link: str | None
