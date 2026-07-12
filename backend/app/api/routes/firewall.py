from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_router_or_404
from app.models.router import Router
from app.schemas.firewall import FirewallStatsResponse, NatStatsResponse
from app.services.firewall_service import get_filter_stats, get_nat_stats
from app.services.router_service import RouterCommandError, RouterConnectionError

router = APIRouter(prefix="/routers", tags=["firewall"])


@router.get("/{router_id}/firewall/filter-stats", response_model=FirewallStatsResponse)
async def filter_stats(router_obj: Router = Depends(get_router_or_404)) -> FirewallStatsResponse:
    try:
        rules = await get_filter_stats(router_obj)
    except (RouterConnectionError, RouterCommandError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return FirewallStatsResponse(router_id=router_obj.id, rules=rules)


@router.get("/{router_id}/firewall/nat-stats", response_model=NatStatsResponse)
async def nat_stats(router_obj: Router = Depends(get_router_or_404)) -> NatStatsResponse:
    try:
        rules = await get_nat_stats(router_obj)
    except (RouterConnectionError, RouterCommandError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return NatStatsResponse(router_id=router_obj.id, rules=rules)
