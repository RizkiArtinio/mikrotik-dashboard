from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_router_or_404
from app.db.session import get_db
from app.models.router import Router
from app.schemas.dashboard import DashboardSnapshot
from app.services.dashboard_service import poll_and_build_snapshot

router = APIRouter(prefix="/routers", tags=["dashboard"])


@router.get("/{router_id}/dashboard", response_model=DashboardSnapshot)
async def get_dashboard(
    router_obj: Router = Depends(get_router_or_404), db: AsyncSession = Depends(get_db)
) -> DashboardSnapshot:
    """REST fallback for the WebSocket dashboard feed — same payload shape."""
    return await poll_and_build_snapshot(db, router_obj)
