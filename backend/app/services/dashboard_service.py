import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interface import Interface
from app.models.router import Router
from app.models.vpn_peer import VpnPeerStatus
from app.schemas.dashboard import DashboardSnapshot, HealthSnapshot, ResourceSnapshot
from app.schemas.interface import InterfaceOut
from app.schemas.vpn_peer import VPNPeerOut
from app.services.router_service import RouterCommandError, RouterConnectionError, RouterService
from app.services.vpn_service import sync_vpn_peers

# Interfaces we care about surfacing on the dashboard/interfaces pages by default.
TRACKED_INTERFACE_PREFIXES = ("ether", "bridge", "vlan", "wireguard")


def _is_tracked(name: str) -> bool:
    return name.startswith(TRACKED_INTERFACE_PREFIXES)


async def _upsert_interfaces(db: AsyncSession, router_id: int, live_interfaces: list[dict]) -> list[Interface]:
    result = await db.execute(select(Interface).where(Interface.router_id == router_id))
    existing = {row.interface_name: row for row in result.scalars().all()}
    now = datetime.now(timezone.utc)
    updated: list[Interface] = []

    for live in live_interfaces:
        name = live["name"]
        if not _is_tracked(name):
            continue

        row = existing.get(name)
        rx_bps = tx_bps = 0
        if row is not None:
            elapsed = (now - row.updated_at.replace(tzinfo=timezone.utc)).total_seconds()
            if elapsed > 0:
                rx_bps = max(0, int((live["rx_bytes"] - row.rx_bytes) * 8 / elapsed))
                tx_bps = max(0, int((live["tx_bytes"] - row.tx_bytes) * 8 / elapsed))
        else:
            row = Interface(router_id=router_id, interface_name=name)
            db.add(row)

        row.interface_type = live["type"]
        row.rx_bps = rx_bps
        row.tx_bps = tx_bps
        row.rx_bytes = live["rx_bytes"]
        row.tx_bytes = live["tx_bytes"]
        row.rx_packets = live["rx_packets"]
        row.tx_packets = live["tx_packets"]
        row.status = "running" if live["running"] and not live["disabled"] else "down"
        updated.append(row)

    await db.commit()
    for row in updated:
        await db.refresh(row)
    return updated


async def poll_and_build_snapshot(db: AsyncSession, router: Router) -> DashboardSnapshot:
    service = RouterService(router)

    try:
        live_resources, live_health, live_interfaces, live_vpn = await asyncio.gather(
            asyncio.to_thread(service.get_resources),
            asyncio.to_thread(service.get_health),
            asyncio.to_thread(service.get_interfaces),
            asyncio.to_thread(service.get_vpn),
        )
    except (RouterConnectionError, RouterCommandError) as exc:
        return DashboardSnapshot(
            router_id=router.id,
            router_name=router.name,
            online=False,
            generated_at=datetime.now(timezone.utc),
            error=str(exc),
        )

    interfaces = await _upsert_interfaces(db, router.id, live_interfaces)
    await sync_vpn_peers(db, router.id, live_vpn)

    result = await db.execute(select(Interface).where(Interface.router_id == router.id))
    all_interfaces = list(result.scalars().all())

    from app.models.vpn_peer import VPNPeer  # local import avoids a cycle with vpn_service

    vpn_result = await db.execute(select(VPNPeer).where(VPNPeer.router_id == router.id))
    vpn_peers = list(vpn_result.scalars().all())

    total_mem = live_resources.get("total_memory") or 0
    free_mem = live_resources.get("free_memory") or 0
    mem_usage = round((1 - free_mem / total_mem) * 100, 1) if total_mem else None

    total_hdd = live_resources.get("total_hdd_space") or 0
    free_hdd = live_resources.get("free_hdd_space") or 0
    disk_usage = round((1 - free_hdd / total_hdd) * 100, 1) if total_hdd else None

    return DashboardSnapshot(
        router_id=router.id,
        router_name=router.name,
        online=True,
        uptime=live_resources.get("uptime"),
        resources=ResourceSnapshot(
            cpu_load=live_resources.get("cpu_load"),
            free_memory=live_resources.get("free_memory"),
            total_memory=live_resources.get("total_memory"),
            memory_usage_percent=mem_usage,
            free_hdd_space=live_resources.get("free_hdd_space"),
            total_hdd_space=live_resources.get("total_hdd_space"),
            disk_usage_percent=disk_usage,
            uptime=live_resources.get("uptime"),
            version=live_resources.get("version"),
            board_name=live_resources.get("board_name"),
            cpu_count=live_resources.get("cpu_count"),
            architecture_name=live_resources.get("architecture_name"),
        ),
        health=HealthSnapshot(
            voltage=live_health.get("voltage"),
            temperature=live_health.get("temperature"),
            cpu_temperature=live_health.get("cpu_temperature"),
        ),
        total_rx_bps=sum(i.rx_bps for i in all_interfaces),
        total_tx_bps=sum(i.tx_bps for i in all_interfaces),
        active_vpn_count=sum(1 for p in vpn_peers if p.status == VpnPeerStatus.connected),
        active_user_count=len(vpn_peers),
        interfaces=[InterfaceOut.model_validate(i) for i in all_interfaces],
        vpn_peers=[VPNPeerOut.model_validate(p) for p in vpn_peers],
        generated_at=datetime.now(timezone.utc),
    )
