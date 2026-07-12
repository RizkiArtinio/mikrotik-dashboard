import asyncio

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_router_or_404
from app.models.router import Router
from app.services.router_service import RouterCommandError, RouterConnectionError, RouterService

router = APIRouter(prefix="/routers", tags=["resources"])


@router.get("/{router_id}/resources")
async def get_resources(router_obj: Router = Depends(get_router_or_404)) -> dict:
    service = RouterService(router_obj)
    try:
        return await asyncio.to_thread(service.get_resources)
    except (RouterConnectionError, RouterCommandError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/{router_id}/health")
async def get_health(router_obj: Router = Depends(get_router_or_404)) -> dict:
    service = RouterService(router_obj)
    try:
        return await asyncio.to_thread(service.get_health)
    except (RouterConnectionError, RouterCommandError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
