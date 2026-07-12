import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.crypto import encrypt_secret
from app.core.security import hash_password
from app.models.alert_rule import AlertRule, AlertType
from app.models.router import Router
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

DEFAULT_ALERT_RULES: list[dict] = [
    {"alert_type": AlertType.router_down, "threshold_value": None, "cooldown_minutes": 15},
    {"alert_type": AlertType.vpn_down, "threshold_value": None, "cooldown_minutes": 15},
    {"alert_type": AlertType.cpu_high, "threshold_value": settings.cpu_alert_threshold, "cooldown_minutes": 15},
    {"alert_type": AlertType.mem_high, "threshold_value": settings.mem_alert_threshold, "cooldown_minutes": 15},
    {"alert_type": AlertType.isp_down, "threshold_value": None, "cooldown_minutes": 15},
]


async def seed_default_admin(db: AsyncSession) -> None:
    result = await db.execute(select(User).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    admin = User(
        email=settings.seed_admin_email,
        full_name="Super Admin",
        hashed_password=hash_password(settings.seed_admin_password),
        role=UserRole.super_admin,
        is_active=True,
    )
    db.add(admin)
    logger.info("Seeded default super admin user: %s", settings.seed_admin_email)


async def seed_default_alert_rules(db: AsyncSession) -> None:
    result = await db.execute(select(AlertRule))
    existing = {row.alert_type for row in result.scalars().all()}

    for rule in DEFAULT_ALERT_RULES:
        if rule["alert_type"] in existing:
            continue
        db.add(AlertRule(**rule))
    if len(existing) < len(DEFAULT_ALERT_RULES):
        logger.info("Seeded default alert rules")


async def seed_default_router(db: AsyncSession) -> None:
    if not settings.seed_default_router:
        return
    result = await db.execute(select(Router).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    router = Router(
        name=settings.default_router_name,
        ip_address=settings.default_router_ip,
        username=settings.default_router_username,
        password_encrypted=encrypt_secret(settings.default_router_password),
        api_port=settings.default_router_api_port,
    )
    db.add(router)
    logger.info("Seeded default router: %s (%s)", router.name, router.ip_address)


async def run_startup_seed(db: AsyncSession) -> None:
    await seed_default_admin(db)
    await seed_default_alert_rules(db)
    await seed_default_router(db)
    await db.commit()
