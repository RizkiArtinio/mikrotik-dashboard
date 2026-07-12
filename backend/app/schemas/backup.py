from datetime import datetime

from pydantic import BaseModel

from app.models.backup import BackupTrigger, BackupType


class BackupOut(BaseModel):
    id: int
    router_id: int
    file_name: str
    file_size: int
    backup_type: BackupType
    triggered_by: BackupTrigger
    backup_date: datetime

    class Config:
        from_attributes = True


class BackupTriggerResponse(BaseModel):
    backups: list[BackupOut]
