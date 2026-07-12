from datetime import datetime

from pydantic import BaseModel

from app.models.alert_rule import AlertType


class AlertRuleOut(BaseModel):
    id: int
    alert_type: AlertType
    threshold_value: float | None
    cooldown_minutes: int
    is_enabled: bool
    notify_telegram: bool
    notify_email: bool
    description: str | None

    class Config:
        from_attributes = True


class AlertRuleUpdate(BaseModel):
    threshold_value: float | None = None
    cooldown_minutes: int | None = None
    is_enabled: bool | None = None
    notify_telegram: bool | None = None
    notify_email: bool | None = None


class NotificationLogOut(BaseModel):
    id: int
    router_id: int | None
    alert_type: str
    target_identifier: str | None
    message: str
    channel: str
    resolved: bool
    sent_at: datetime

    class Config:
        from_attributes = True
