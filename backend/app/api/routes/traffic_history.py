from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_router_or_404
from app.db.session import get_db
from app.models.router import Router
from app.schemas.traffic_history import BandwidthHistoryResponse, BandwidthRange, TrafficHistoryPoint
from app.services.traffic_service import get_bandwidth_history

router = APIRouter(prefix="/routers", tags=["traffic-history"])


@router.get("/{router_id}/traffic-history", response_model=BandwidthHistoryResponse)
async def bandwidth_history(
    interface: str = Query(..., description="Interface name, e.g. ether1"),
    range: BandwidthRange = Query("day"),
    router_obj: Router = Depends(get_router_or_404),
    db: AsyncSession = Depends(get_db),
) -> BandwidthHistoryResponse:
    if range not in ("day", "week", "month"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="range must be day, week, or month")

    rows = await get_bandwidth_history(db, router_obj.id, interface, range)
    return BandwidthHistoryResponse(
        router_id=router_obj.id,
        interface_name=interface,
        range=range,
        points=[TrafficHistoryPoint(timestamp=r.timestamp, rx=r.rx, tx=r.tx) for r in rows],
    )
