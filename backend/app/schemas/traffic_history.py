from datetime import datetime
from typing import Literal

from pydantic import BaseModel

BandwidthRange = Literal["day", "week", "month"]


class TrafficHistoryPoint(BaseModel):
    timestamp: datetime
    rx: int
    tx: int


class BandwidthHistoryResponse(BaseModel):
    router_id: int
    interface_name: str
    range: BandwidthRange
    points: list[TrafficHistoryPoint]
