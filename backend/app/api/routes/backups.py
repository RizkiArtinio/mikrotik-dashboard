from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_router_or_404
from app.core.security import require_engineer_or_admin
from app.db.session import get_db
from app.models.backup import Backup, BackupTrigger
from app.models.router import Router
from app.schemas.backup import BackupOut
from app.services.backup_service import BackupServiceError, run_backup

router = APIRouter(tags=["backups"])


@router.post(
    "/routers/{router_id}/backups",
    response_model=list[BackupOut],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_engineer_or_admin)],
)
async def trigger_backup(
    router_obj: Router = Depends(get_router_or_404), db: AsyncSession = Depends(get_db)
) -> list[Backup]:
    try:
        return await run_backup(db, router_obj, BackupTrigger.manual)
    except BackupServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/routers/{router_id}/backups", response_model=list[BackupOut])
async def list_backups(
    router_obj: Router = Depends(get_router_or_404), db: AsyncSession = Depends(get_db)
) -> list[Backup]:
    result = await db.execute(
        select(Backup).where(Backup.router_id == router_obj.id).order_by(Backup.backup_date.desc())
    )
    return list(result.scalars().all())


@router.get("/backups/{backup_id}/download")
async def download_backup(backup_id: int, db: AsyncSession = Depends(get_db)) -> FileResponse:
    result = await db.execute(select(Backup).where(Backup.id == backup_id))
    backup = result.scalar_one_or_none()
    if backup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup not found")
    return FileResponse(backup.file_path, filename=backup.file_name, media_type="application/octet-stream")
