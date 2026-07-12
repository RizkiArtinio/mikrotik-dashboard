from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_router_or_404
from app.models.router import Router
from app.schemas.ppp_hotspot import HotspotUsersResponse, PppUsersResponse
from app.services.ppp_hotspot_service import get_hotspot_users, get_ppp_users
from app.services.router_service import RouterCommandError, RouterConnectionError

router = APIRouter(prefix="/routers", tags=["users"])


@router.get("/{router_id}/ppp-users", response_model=PppUsersResponse)
async def ppp_users(router_obj: Router = Depends(get_router_or_404)) -> PppUsersResponse:
    try:
        users = await get_ppp_users(router_obj)
    except (RouterConnectionError, RouterCommandError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return PppUsersResponse(router_id=router_obj.id, users=users)


@router.get("/{router_id}/hotspot-users", response_model=HotspotUsersResponse)
async def hotspot_users(router_obj: Router = Depends(get_router_or_404)) -> HotspotUsersResponse:
    try:
        users = await get_hotspot_users(router_obj)
    except (RouterConnectionError, RouterCommandError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return HotspotUsersResponse(router_id=router_obj.id, users=users)
