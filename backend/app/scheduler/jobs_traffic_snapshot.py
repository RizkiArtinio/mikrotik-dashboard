import logging

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.interface import Interface
from app.models.router import Router
from app.services.traffic_service import snapshot_interfaces

logger = logging.getLogger(__name__)


async def snapshot_all_routers() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Router.id).where(Router.is_active.is_(True)))
        router_ids = [row[0] for row in result.all()]

        for router_id in router_ids:
            iface_result = await db.execute(select(Interface).where(Interface.router_id == router_id))
            interfaces = [
                {"interface_name": i.interface_name, "rx_bytes": i.rx_bytes, "tx_bytes": i.tx_bytes}
                for i in iface_result.scalars().all()
            ]
            if interfaces:
                await snapshot_interfaces(db, router_id, interfaces)
