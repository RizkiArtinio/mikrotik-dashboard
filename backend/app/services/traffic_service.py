from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.traffic_history import TrafficHistory
from app.utils.datetime_utils import range_start


async def get_bandwidth_history(
    db: AsyncSession, router_id: int, interface_name: str, range_key: str
) -> list[TrafficHistory]:
    since = range_start(range_key)
    result = await db.execute(
        select(TrafficHistory)
        .where(
            TrafficHistory.router_id == router_id,
            TrafficHistory.interface_name == interface_name,
            TrafficHistory.timestamp >= since,
        )
        .order_by(TrafficHistory.timestamp.asc())
    )
    return list(result.scalars().all())


async def snapshot_interfaces(db: AsyncSession, router_id: int, interfaces: list[dict]) -> None:
    """Insert one TrafficHistory row per interface from the latest polled counters."""
    for iface in interfaces:
        db.add(
            TrafficHistory(
                router_id=router_id,
                interface_name=iface["interface_name"],
                rx=iface["rx_bytes"],
                tx=iface["tx_bytes"],
            )
        )
    await db.commit()
