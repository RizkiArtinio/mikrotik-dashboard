import asyncio

from app.models.router import Router
from app.services.router_service import RouterService


async def get_ppp_users(router: Router) -> list[dict]:
    service = RouterService(router)
    return await asyncio.to_thread(service.get_ppp_active)


async def get_hotspot_users(router: Router) -> list[dict]:
    service = RouterService(router)
    return await asyncio.to_thread(service.get_hotspot_active)
