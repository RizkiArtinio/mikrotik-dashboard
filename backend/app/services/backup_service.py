import asyncio
import logging
from datetime import datetime, timezone

import paramiko
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.crypto import decrypt_secret
from app.models.backup import Backup, BackupTrigger, BackupType
from app.models.router import Router
from app.services.router_service import RouterCommandError, RouterConnectionError, RouterService
from app.utils.file_utils import file_size_bytes, router_backup_dir

logger = logging.getLogger(__name__)


class BackupServiceError(Exception):
    pass


def _fetch_via_sftp(router: Router, remote_filename: str, local_path: str) -> None:
    transport = paramiko.Transport((router.ip_address, 22))
    try:
        transport.connect(username=router.username, password=decrypt_secret(router.password_encrypted))
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.get(remote_filename, local_path)
        finally:
            sftp.close()
    finally:
        transport.close()


async def run_backup(db: AsyncSession, router: Router, triggered_by: BackupTrigger) -> list[Backup]:
    service = RouterService(router)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base_name = f"{timestamp}_{router.name.replace(' ', '_')}"

    try:
        result = await asyncio.to_thread(service.create_backup, base_name)
    except (RouterConnectionError, RouterCommandError) as exc:
        raise BackupServiceError(f"Backup failed for router {router.id}: {exc}") from exc

    # Give RouterOS a moment to flush the files to disk before fetching.
    await asyncio.sleep(2)

    local_dir = router_backup_dir(settings.backup_storage_dir, router.id)
    created: list[Backup] = []

    for remote_name, backup_type in (
        (result["backup_file"], BackupType.backup),
        (result["rsc_file"], BackupType.rsc),
    ):
        local_path = local_dir / remote_name
        try:
            await asyncio.to_thread(_fetch_via_sftp, router, remote_name, str(local_path))
        except Exception as exc:
            logger.error("Failed to fetch %s from router %s via SFTP: %s", remote_name, router.id, exc)
            continue

        backup = Backup(
            router_id=router.id,
            file_name=remote_name,
            file_path=str(local_path),
            file_size=file_size_bytes(local_path),
            backup_type=backup_type,
            triggered_by=triggered_by,
        )
        db.add(backup)
        created.append(backup)

    if not created:
        raise BackupServiceError(
            f"Router {router.id} generated backup files but none could be retrieved via SFTP "
            "(check that SFTP/SSH is enabled on the router and reachable)."
        )

    await db.commit()
    for backup in created:
        await db.refresh(backup)
    return created
