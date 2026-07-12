from datetime import datetime

from pydantic import BaseModel, Field


class RouterCreate(BaseModel):
    name: str
    ip_address: str
    username: str
    password: str = Field(..., description="Plaintext router password — encrypted before storage")
    api_port: int = 8728
    use_ssl: bool = False
    site: str | None = None
    isp_gateway: str | None = None
    wireguard_endpoint: str | None = None


class RouterUpdate(BaseModel):
    name: str | None = None
    ip_address: str | None = None
    username: str | None = None
    password: str | None = None
    api_port: int | None = None
    use_ssl: bool | None = None
    site: str | None = None
    isp_gateway: str | None = None
    wireguard_endpoint: str | None = None
    is_active: bool | None = None


class RouterOut(BaseModel):
    id: int
    name: str
    ip_address: str
    username: str
    api_port: int
    use_ssl: bool
    site: str | None
    isp_gateway: str | None
    wireguard_endpoint: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConnectionTestResult(BaseModel):
    success: bool
    message: str
    identity: str | None = None
    routeros_version: str | None = None
