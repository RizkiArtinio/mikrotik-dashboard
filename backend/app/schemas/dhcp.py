from pydantic import BaseModel


class DhcpLease(BaseModel):
    hostname: str | None = None
    mac_address: str
    ip_address: str
    status: str | None = None
    expires_after: str | None = None


class DhcpLeaseResponse(BaseModel):
    router_id: int
    leases: list[DhcpLease]
