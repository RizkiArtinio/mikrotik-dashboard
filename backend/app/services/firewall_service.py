import asyncio

from app.models.router import Router
from app.services.router_service import RouterService


async def get_filter_stats(router: Router) -> list[dict]:
    service = RouterService(router)
    return await asyncio.to_thread(service.get_firewall)


async def get_nat_stats(router: Router) -> list[dict]:
    service = RouterService(router)
    return await asyncio.to_thread(service.get_nat)
