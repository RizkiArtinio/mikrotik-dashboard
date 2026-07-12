from pydantic import BaseModel


class DhcpLease(BaseModel):
    hostname: str | None = None
    # RouterOS can report leases without a MAC (e.g. static/reserved entries
    # not yet bound to a device) or without an address (e.g. "waiting"
    # status), so neither is guaranteed non-null in practice.
    mac_address: str | None = None
    ip_address: str | None = None
    status: str | None = None
    expires_after: str | None = None


class DhcpLeaseResponse(BaseModel):
    router_id: int
    leases: list[DhcpLease]
