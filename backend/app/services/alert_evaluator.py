import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert_rule import AlertRule, AlertType
from app.models.notification_log import NotificationLog
from app.models.router import Router
from app.services.notifiers.base_notifier import Notifier
from app.services.notifiers.email_notifier import EmailNotifier
from app.services.notifiers.telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)

NOTIFIERS: list[Notifier] = [TelegramNotifier(), EmailNotifier()]


class AlertCondition:
    def __init__(self, alert_type: AlertType, dedup_key: str, target: str | None, message: str):
        self.alert_type = alert_type
        self.dedup_key = dedup_key
        self.target = target
        self.message = message


async def _in_cooldown(db: AsyncSession, dedup_key: str, cooldown_minutes: int) -> bool:
    result = await db.execute(
        select(NotificationLog)
        .where(NotificationLog.dedup_key == dedup_key)
        .order_by(NotificationLog.sent_at.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    if last is None:
        return False
    return datetime.now(timezone.utc) - last.sent_at.replace(tzinfo=timezone.utc) < timedelta(
        minutes=cooldown_minutes
    )


async def _dispatch(db: AsyncSession, router_id: int | None, rule: AlertRule, condition: AlertCondition) -> None:
    if await _in_cooldown(db, condition.dedup_key, rule.cooldown_minutes):
        return

    subject = condition.alert_type.value.replace("_", " ").title()
    sent_any = False

    if rule.notify_telegram:
        sent_any |= await NOTIFIERS[0].send(subject, condition.message)
    if rule.notify_email:
        sent_any |= await NOTIFIERS[1].send(subject, condition.message)

    db.add(
        NotificationLog(
            router_id=router_id,
            alert_type=condition.alert_type.value,
            dedup_key=condition.dedup_key,
            target_identifier=condition.target,
            message=condition.message,
            channel="telegram+email" if sent_any else "none-configured",
        )
    )
    await db.commit()
    logger.info("Alert dispatched: %s (%s)", condition.alert_type.value, condition.dedup_key)


def _conditions_for(
    router: Router,
    *,
    online: bool,
    resources: dict | None,
    vpn_peers: list[dict],
    isp_results: list[dict],
    mem_threshold: float,
    cpu_threshold: float,
) -> dict[AlertType, list[AlertCondition]]:
    conditions: dict[AlertType, list[AlertCondition]] = {t: [] for t in AlertType}

    if not online:
        conditions[AlertType.router_down].append(
            AlertCondition(
                AlertType.router_down,
                f"router_down:{router.id}",
                router.name,
                f"Router '{router.name}' ({router.ip_address}) is unreachable.",
            )
        )
        return conditions

    if resources:
        cpu_load = resources.get("cpu_load") or 0
        if cpu_load > cpu_threshold:
            conditions[AlertType.cpu_high].append(
                AlertCondition(
                    AlertType.cpu_high,
                    f"cpu_high:{router.id}",
                    router.name,
                    f"Router '{router.name}' CPU load is {cpu_load:.0f}% (threshold {cpu_threshold:.0f}%).",
                )
            )

        total_mem = resources.get("total_memory") or 0
        free_mem = resources.get("free_memory") or 0
        if total_mem > 0:
            mem_usage = (1 - free_mem / total_mem) * 100
            if mem_usage > mem_threshold:
                conditions[AlertType.mem_high].append(
                    AlertCondition(
                        AlertType.mem_high,
                        f"mem_high:{router.id}",
                        router.name,
                        f"Router '{router.name}' memory usage is {mem_usage:.0f}% (threshold {mem_threshold:.0f}%).",
                    )
                )

    for peer in vpn_peers:
        if peer.get("status") == "disconnected":
            conditions[AlertType.vpn_down].append(
                AlertCondition(
                    AlertType.vpn_down,
                    f"vpn_down:{router.id}:{peer.get('peer_name')}",
                    peer.get("peer_name"),
                    f"VPN peer '{peer.get('peer_name')}' on router '{router.name}' is disconnected.",
                )
            )

    for isp in isp_results:
        if isp.get("status") == "down":
            conditions[AlertType.isp_down].append(
                AlertCondition(
                    AlertType.isp_down,
                    f"isp_down:{router.id}:{isp.get('target')}",
                    isp.get("target"),
                    f"ISP target '{isp.get('label')}' ({isp.get('target')}) is unreachable from router '{router.name}'.",
                )
            )

    return conditions


async def evaluate(
    db: AsyncSession,
    router: Router,
    *,
    online: bool,
    resources: dict | None = None,
    vpn_peers: list[dict] | None = None,
    isp_results: list[dict] | None = None,
) -> None:
    result = await db.execute(select(AlertRule))
    rules = {rule.alert_type: rule for rule in result.scalars().all()}

    conditions = _conditions_for(
        router,
        online=online,
        resources=resources,
        vpn_peers=vpn_peers or [],
        isp_results=isp_results or [],
        cpu_threshold=rules[AlertType.cpu_high].threshold_value if AlertType.cpu_high in rules else 90,
        mem_threshold=rules[AlertType.mem_high].threshold_value if AlertType.mem_high in rules else 90,
    )

    for alert_type, items in conditions.items():
        rule = rules.get(alert_type)
        if rule is None or not rule.is_enabled:
            continue
        for condition in items:
            await _dispatch(db, router.id, rule, condition)
