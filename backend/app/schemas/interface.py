from datetime import datetime

from pydantic import BaseModel


class InterfaceOut(BaseModel):
    id: int
    router_id: int
    interface_name: str
    interface_type: str
    rx_bps: int
    tx_bps: int
    rx_bytes: int
    tx_bytes: int
    rx_packets: int
    tx_packets: int
    status: str
    updated_at: datetime

    class Config:
        from_attributes = True
