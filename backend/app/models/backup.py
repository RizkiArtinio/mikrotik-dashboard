import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BackupType(str, enum.Enum):
    backup = "backup"
    rsc = "rsc"


class BackupTrigger(str, enum.Enum):
    manual = "manual"
    scheduled = "scheduled"


class Backup(Base):
    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    router_id: Mapped[int] = mapped_column(ForeignKey("routers.id", ondelete="CASCADE"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    backup_type: Mapped[BackupType] = mapped_column(Enum(BackupType), nullable=False)
    triggered_by: Mapped[BackupTrigger] = mapped_column(Enum(BackupTrigger), default=BackupTrigger.manual)
    backup_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    router: Mapped["Router"] = relationship(back_populates="backups")  # noqa: F821
