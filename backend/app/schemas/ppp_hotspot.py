from pydantic import BaseModel


class PppUser(BaseModel):
    username: str
    service: str | None = None
    caller_id: str | None = None
    address: str | None = None
    login_time: str | None = None
    bytes_in: int = 0
    bytes_out: int = 0


class HotspotUser(BaseModel):
    username: str
    address: str | None = None
    mac_address: str | None = None
    login_time: str | None = None
    bytes_in: int = 0
    bytes_out: int = 0
    uptime: str | None = None


class PppUsersResponse(BaseModel):
    router_id: int
    users: list[PppUser]


class HotspotUsersResponse(BaseModel):
    router_id: int
    users: list[HotspotUser]
