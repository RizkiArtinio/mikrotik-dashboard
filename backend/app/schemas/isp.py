from pydantic import BaseModel


class IspPingResult(BaseModel):
    target: str
    label: str
    latency_ms: float | None = None
    packet_loss_percent: float | None = None
    status: str  # "up" | "down"


class IspStatusResponse(BaseModel):
    router_id: int
    results: list[IspPingResult]
