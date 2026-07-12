from fastapi import APIRouter, Depends

from app.core.deps import get_router_or_404
from app.models.router import Router
from app.schemas.isp import IspStatusResponse
from app.services.isp_ping_service import check_isp_status

router = APIRouter(prefix="/routers", tags=["isp"])


@router.get("/{router_id}/isp-status", response_model=IspStatusResponse)
async def isp_status(router_obj: Router = Depends(get_router_or_404)) -> IspStatusResponse:
    results = await check_isp_status(router_obj)
    return IspStatusResponse(router_id=router_obj.id, results=results)
