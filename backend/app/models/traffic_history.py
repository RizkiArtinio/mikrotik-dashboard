from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TrafficHistory(Base):
    """Time-series snapshot of interface counters, written periodically by the scheduler.

    Backs the per-day/week/month bandwidth charts (queried via GROUP BY on `timestamp`).
    """

    __tablename__ = "traffic_history"
    __table_args__ = (
        Index("ix_traffic_history_router_iface_ts", "router_id", "interface_name", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    router_id: Mapped[int] = mapped_column(ForeignKey("routers.id", ondelete="CASCADE"), nullable=False)
    interface_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rx: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    tx: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
