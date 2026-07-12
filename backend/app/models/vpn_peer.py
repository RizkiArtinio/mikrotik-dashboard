import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VpnType(str, enum.Enum):
    wireguard = "wireguard"
    l2tp = "l2tp"
    sstp = "sstp"
    openvpn = "openvpn"
    ipsec = "ipsec"


class VpnPeerStatus(str, enum.Enum):
    connected = "connected"
    disconnected = "disconnected"
    configured = "configured"
    unknown = "unknown"


class VPNPeer(Base):
    __tablename__ = "vpn_peers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    router_id: Mapped[int] = mapped_column(ForeignKey("routers.id", ondelete="CASCADE"), nullable=False)

    peer_name: Mapped[str] = mapped_column(String(150), nullable=False)
    vpn_type: Mapped[VpnType] = mapped_column(Enum(VpnType), nullable=False)
    public_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    allowed_ip: Mapped[str | None] = mapped_column(String(100), nullable=True)
    endpoint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dns: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    remote_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    status: Mapped[VpnPeerStatus] = mapped_column(Enum(VpnPeerStatus), default=VpnPeerStatus.unknown)
    rx_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    tx_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    router: Mapped["Router"] = relationship(back_populates="vpn_peers")  # noqa: F821
