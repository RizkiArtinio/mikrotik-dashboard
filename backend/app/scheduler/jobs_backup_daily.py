import logging

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.backup import BackupTrigger
from app.models.router import Router
from app.services.backup_service import BackupServiceError, run_backup

logger = logging.getLogger(__name__)


async def run_daily_backups() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Router).where(Router.is_active.is_(True)))
        routers = list(result.scalars().all())

    for router in routers:
        async with AsyncSessionLocal() as db:
            router = await db.get(Router, router.id)
            try:
                await run_backup(db, router, BackupTrigger.scheduled)
                logger.info("Scheduled backup completed for router %s", router.id)
            except BackupServiceError:
                logger.exception("Scheduled backup failed for router %s", router.id)
