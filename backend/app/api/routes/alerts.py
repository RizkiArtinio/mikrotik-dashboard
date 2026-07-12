from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_super_admin
from app.db.session import get_db
from app.models.alert_rule import AlertRule
from app.models.notification_log import NotificationLog
from app.schemas.alert import AlertRuleOut, AlertRuleUpdate, NotificationLogOut

router = APIRouter(tags=["alerts"])


@router.get("/alert-rules", response_model=list[AlertRuleOut])
async def list_alert_rules(db: AsyncSession = Depends(get_db)) -> list[AlertRule]:
    result = await db.execute(select(AlertRule).order_by(AlertRule.alert_type))
    return list(result.scalars().all())


@router.put(
    "/alert-rules/{rule_id}", response_model=AlertRuleOut, dependencies=[Depends(require_super_admin)]
)
async def update_alert_rule(
    rule_id: int, payload: AlertRuleUpdate, db: AsyncSession = Depends(get_db)
) -> AlertRule:
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("/notification-log", response_model=list[NotificationLogOut])
async def notification_log(limit: int = 100, db: AsyncSession = Depends(get_db)) -> list[NotificationLog]:
    result = await db.execute(
        select(NotificationLog).order_by(NotificationLog.sent_at.desc()).limit(limit)
    )
    return list(result.scalars().all())
