from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_router_or_404
from app.models.router import Router
from app.schemas.dhcp import DhcpLeaseResponse
from app.services.dhcp_service import get_dhcp_leases
from app.services.router_service import RouterCommandError, RouterConnectionError

router = APIRouter(prefix="/routers", tags=["dhcp"])


@router.get("/{router_id}/dhcp/leases", response_model=DhcpLeaseResponse)
async def dhcp_leases(router_obj: Router = Depends(get_router_or_404)) -> DhcpLeaseResponse:
    try:
        leases = await get_dhcp_leases(router_obj)
    except (RouterConnectionError, RouterCommandError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return DhcpLeaseResponse(router_id=router_obj.id, leases=leases)
