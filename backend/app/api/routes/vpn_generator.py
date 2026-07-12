from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_router_or_404
from app.core.security import require_engineer_or_admin
from app.db.session import get_db
from app.models.router import Router
from app.models.user import User
from app.schemas.vpn_peer import WireguardPeerCreate, WireguardPeerResult
from app.services.vpn_service import VpnServiceError, create_wireguard_peer

router = APIRouter(prefix="/routers", tags=["vpn-generator"])


@router.post(
    "/{router_id}/vpn/wireguard-peer",
    response_model=WireguardPeerResult,
    status_code=status.HTTP_201_CREATED,
)
async def generate_wireguard_peer(
    payload: WireguardPeerCreate,
    router_obj: Router = Depends(get_router_or_404),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_engineer_or_admin),
) -> WireguardPeerResult:
    try:
        return await create_wireguard_peer(db, router_obj, payload, created_by_user_id=current_user.id)
    except VpnServiceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
