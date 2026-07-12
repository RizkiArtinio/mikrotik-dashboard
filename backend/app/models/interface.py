from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Interface(Base):
    """Latest polled snapshot for one router interface (upserted every poll cycle).

    Historical rx/tx over time lives in TrafficHistory, not here.
    """

    __tablename__ = "interfaces"
    __table_args__ = (UniqueConstraint("router_id", "interface_name", name="uq_interface_router_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    router_id: Mapped[int] = mapped_column(ForeignKey("routers.id", ondelete="CASCADE"), nullable=False)
    interface_name: Mapped[str] = mapped_column(String(100), nullable=False)
    interface_type: Mapped[str] = mapped_column(String(30), nullable=False, default="ether")

    rx_bps: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    tx_bps: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    rx_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    tx_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    rx_packets: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    tx_packets: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="unknown", nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    router: Mapped["Router"] = relationship(back_populates="interfaces")  # noqa: F821
