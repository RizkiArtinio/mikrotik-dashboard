from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_router_or_404
from app.db.session import get_db
from app.models.router import Router
from app.models.vpn_peer import VPNPeer
from app.schemas.vpn_peer import VPNPeerOut

router = APIRouter(prefix="/routers", tags=["vpn"])


@router.get("/{router_id}/vpn", response_model=list[VPNPeerOut])
async def list_vpn_peers(
    router_obj: Router = Depends(get_router_or_404), db: AsyncSession = Depends(get_db)
) -> list[VPNPeer]:
    result = await db.execute(
        select(VPNPeer).where(VPNPeer.router_id == router_obj.id).order_by(VPNPeer.vpn_type, VPNPeer.peer_name)
    )
    return list(result.scalars().all())
