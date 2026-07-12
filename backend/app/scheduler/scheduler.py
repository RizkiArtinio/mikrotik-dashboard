import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.scheduler.jobs_backup_daily import run_daily_backups
from app.scheduler.jobs_poll_router import poll_all_routers
from app.scheduler.jobs_traffic_snapshot import snapshot_all_routers

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def configure_scheduler() -> AsyncIOScheduler:
    scheduler.add_job(
        poll_all_routers,
        trigger=IntervalTrigger(seconds=settings.dashboard_poll_interval_seconds),
        id="poll_all_routers",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        snapshot_all_routers,
        trigger=IntervalTrigger(minutes=settings.traffic_snapshot_interval_minutes),
        id="snapshot_all_routers",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        run_daily_backups,
        trigger=CronTrigger(hour=settings.backup_daily_hour, minute=settings.backup_daily_minute),
        id="run_daily_backups",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    return scheduler


def start_scheduler() -> None:
    configure_scheduler()
    scheduler.start()
    logger.info(
        "Scheduler started: dashboard poll every %ss, traffic snapshot every %sm, daily backup at %02d:%02d",
        settings.dashboard_poll_interval_seconds,
        settings.traffic_snapshot_interval_minutes,
        settings.backup_daily_hour,
        settings.backup_daily_minute,
    )


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
