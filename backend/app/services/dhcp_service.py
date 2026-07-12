import asyncio

from app.models.router import Router
from app.services.router_service import RouterService


async def get_dhcp_leases(router: Router) -> list[dict]:
    service = RouterService(router)
    return await asyncio.to_thread(service.get_dhcp_leases)
