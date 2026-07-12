from datetime import datetime

from pydantic import BaseModel

from app.schemas.interface import InterfaceOut
from app.schemas.vpn_peer import VPNPeerOut


class ResourceSnapshot(BaseModel):
    cpu_load: float | None = None
    free_memory: int | None = None
    total_memory: int | None = None
    memory_usage_percent: float | None = None
    free_hdd_space: int | None = None
    total_hdd_space: int | None = None
    disk_usage_percent: float | None = None
    uptime: str | None = None
    version: str | None = None
    board_name: str | None = None
    cpu_count: int | None = None
    architecture_name: str | None = None


class HealthSnapshot(BaseModel):
    voltage: float | None = None
    temperature: float | None = None
    cpu_temperature: float | None = None


class DashboardSnapshot(BaseModel):
    router_id: int
    router_name: str
    online: bool
    uptime: str | None = None
    resources: ResourceSnapshot | None = None
    health: HealthSnapshot | None = None
    total_rx_bps: int = 0
    total_tx_bps: int = 0
    active_vpn_count: int = 0
    active_user_count: int = 0
    interfaces: list[InterfaceOut] = []
    vpn_peers: list[VPNPeerOut] = []
    generated_at: datetime
    error: str | None = None
