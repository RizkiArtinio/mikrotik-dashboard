import enum

from sqlalchemy import Boolean, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AlertType(str, enum.Enum):
    router_down = "router_down"
    vpn_down = "vpn_down"
    cpu_high = "cpu_high"
    mem_high = "mem_high"
    isp_down = "isp_down"


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType), unique=True, nullable=False)
    threshold_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_telegram: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
