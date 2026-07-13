from datetime import datetime

from pydantic import BaseModel, Field

from app.models.vpn_peer import VpnPeerStatus, VpnType


class WireguardPeerCreate(BaseModel):
    username: str = Field(..., description="Human-readable peer/user name")
    allowed_ip: str | None = Field(
        default=None,
        description="e.g. 10.10.10.5/32. Leave empty to auto-assign the next free IP from "
        "Router.wireguard_pool_name.",
    )
    dns: str = Field(default="1.1.1.1")
    endpoint: str | None = Field(
        default=None, description="Router's public endpoint host:port; defaults to Router.wireguard_endpoint"
    )
    description: str | None = None


class WireguardPeerResult(BaseModel):
    peer: "VPNPeerOut"
    config_text: str
    qr_code_base64: str


class L2tpPeerCreate(BaseModel):
    username: str | None = Field(default=None, description="Leave empty to auto-generate")
    password: str | None = Field(default=None, description="Leave empty to auto-generate")
    description: str | None = None


class L2tpPeerResult(BaseModel):
    peer: "VPNPeerOut"
    server_address: str
    username: str
    password: str
    ipsec_psk: str | None


class OvpnPeerCreate(BaseModel):
    username: str | None = Field(default=None, description="Leave empty to auto-generate")
    password: str | None = Field(default=None, description="Leave empty to auto-generate")
    description: str | None = None


class OvpnPeerResult(BaseModel):
    peer: "VPNPeerOut"
    config_text: str
    username: str
    password: str


class VPNPeerOut(BaseModel):
    id: int
    router_id: int
    peer_name: str
    vpn_type: VpnType
    public_key: str | None
    allowed_ip: str | None
    endpoint: str | None
    dns: str | None
    description: str | None
    remote_address: str | None
    status: VpnPeerStatus
    rx_bytes: int
    tx_bytes: int
    last_seen: datetime | None

    class Config:
        from_attributes = True


WireguardPeerResult.model_rebuild()
L2tpPeerResult.model_rebuild()
OvpnPeerResult.model_rebuild()
