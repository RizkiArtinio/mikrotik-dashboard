from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Router(Base):
    __tablename__ = "routers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    password_encrypted: Mapped[str] = mapped_column(String(512), nullable=False)
    api_port: Mapped[int] = mapped_column(Integer, default=8728, nullable=False)
    use_ssl: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    site: Mapped[str | None] = mapped_column(String(150), nullable=True)
    isp_gateway: Mapped[str | None] = mapped_column(String(45), nullable=True)
    wireguard_endpoint: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Reserved for future SNMP polling path — unused in v1.
    snmp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    snmp_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    snmp_community_encrypted: Mapped[str | None] = mapped_column(String(512), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    interfaces: Mapped[list["Interface"]] = relationship(  # noqa: F821
        back_populates="router", cascade="all, delete-orphan"
    )
    vpn_peers: Mapped[list["VPNPeer"]] = relationship(  # noqa: F821
        back_populates="router", cascade="all, delete-orphan"
    )
    backups: Mapped[list["Backup"]] = relationship(  # noqa: F821
        back_populates="router", cascade="all, delete-orphan"
    )
