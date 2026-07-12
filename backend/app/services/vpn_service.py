import asyncio
import ipaddress
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.router import Router
from app.models.vpn_peer import VPNPeer, VpnPeerStatus, VpnType
from app.schemas.vpn_peer import VPNPeerOut, WireguardPeerCreate, WireguardPeerResult
from app.services.qr_service import generate_qr_base64
from app.services.router_service import RouterCommandError, RouterService
from app.services.wireguard_keygen import generate_keypair


class VpnServiceError(Exception):
    pass


def _parse_pool_ranges(ranges: str) -> list[tuple[ipaddress.IPv4Address, ipaddress.IPv4Address]]:
    """RouterOS /ip/pool "ranges" is e.g. "172.30.30.110-172.30.30.160" or a
    comma-separated list of such ranges for a non-contiguous pool."""
    parsed = []
    for chunk in ranges.split(","):
        chunk = chunk.strip()
        if "-" not in chunk:
            continue
        start, end = chunk.split("-", 1)
        parsed.append((ipaddress.IPv4Address(start.strip()), ipaddress.IPv4Address(end.strip())))
    return parsed


def find_available_ip(service: RouterService, pool_name: str) -> str:
    """Auto-assign the next free IP from an existing RouterOS /ip pool
    (e.g. "vpn-pool"), so operators don't have to hand-pick one per peer.
    Deliberately reuses a pool the router already has (rather than a
    dashboard-only subnet) so the assigned address inherits whatever
    NAT/forward rules the admin already set up for that range — no new
    firewall rules needed for internet/LAN access to work."""
    pools = service.get_ip_pools()
    pool = next((p for p in pools if p["name"] == pool_name), None)
    if pool is None:
        raise VpnServiceError(
            f"IP pool '{pool_name}' not found on this router. Check Router.wireguard_pool_name "
            "matches an existing /ip pool name, or provide allowed_ip manually."
        )

    ranges = _parse_pool_ranges(pool["ranges"])
    if not ranges:
        raise VpnServiceError(f"IP pool '{pool_name}' has no usable ranges.")

    used: set[str] = set()
    for peer in service.get_wireguard_peers():
        addr = peer.get("allowed_address")
        if addr:
            used.add(addr.split("/")[0])
    for lease in service.get_dhcp_leases():
        if lease.get("ip_address"):
            used.add(lease["ip_address"])
    for addr in service.get_ip_addresses():
        if addr.get("address"):
            used.add(addr["address"].split("/")[0])

    for start, end in ranges:
        ip_int = int(start)
        end_int = int(end)
        while ip_int <= end_int:
            candidate = str(ipaddress.IPv4Address(ip_int))
            if candidate not in used:
                return f"{candidate}/32"
            ip_int += 1

    raise VpnServiceError(f"IP pool '{pool_name}' is exhausted — no free address available.")


def _build_client_config(
    *, client_private_key: str, allowed_ip: str, dns: str, router_public_key: str, endpoint: str
) -> str:
    client_address = allowed_ip.split("/")[0]
    return (
        "[Interface]\n"
        f"PrivateKey = {client_private_key}\n"
        f"Address = {client_address}/32\n"
        f"DNS = {dns}\n\n"
        "[Peer]\n"
        f"PublicKey = {router_public_key}\n"
        f"Endpoint = {endpoint}\n"
        "AllowedIPs = 0.0.0.0/0\n"
        "PersistentKeepalive = 25\n"
    )


async def create_wireguard_peer(
    db: AsyncSession, router: Router, payload: WireguardPeerCreate, created_by_user_id: int
) -> WireguardPeerResult:
    service = RouterService(router)

    interfaces = await asyncio.to_thread(service.get_interfaces)
    wg_interfaces = [i for i in interfaces if i["type"] == "wireguard"]
    if not wg_interfaces:
        raise VpnServiceError(
            "No WireGuard interface configured on this router. Create one under "
            "/interface/wireguard on the router first."
        )
    wg_interface_name = wg_interfaces[0]["name"]

    router_public_key = await asyncio.to_thread(
        service.get_wireguard_interface_public_key, wg_interface_name
    )
    if not router_public_key:
        raise VpnServiceError(f"Could not read public key for interface {wg_interface_name}")

    endpoint = payload.endpoint or router.wireguard_endpoint
    if not endpoint:
        raise VpnServiceError(
            "No endpoint provided and Router.wireguard_endpoint is not configured. "
            "Set the router's public IP/hostname + WireGuard port first."
        )

    if payload.allowed_ip:
        allowed_ip = payload.allowed_ip
    elif router.wireguard_pool_name:
        allowed_ip = await asyncio.to_thread(find_available_ip, service, router.wireguard_pool_name)
    else:
        raise VpnServiceError(
            "No allowed_ip provided and Router.wireguard_pool_name is not configured. "
            "Set it in Admin → Routers (name of an existing /ip pool, e.g. 'vpn-pool'), "
            "or provide allowed_ip manually."
        )

    client_private_key, client_public_key = generate_keypair()

    try:
        await asyncio.to_thread(
            service.create_wireguard_peer,
            wg_interface_name,
            client_public_key,
            allowed_ip,
            # Always the username, never the description: sync_vpn_peers()
            # matches DB rows to live router peers by reading this same
            # comment field back as `peer_name` on every poll (see
            # RouterService.get_wireguard_peers). If this ever diverges from
            # the peer_name used below when inserting the VPNPeer row, the
            # next poll won't recognize it as the same peer and will insert
            # a duplicate row instead of updating this one.
            payload.username,
        )
    except RouterCommandError as exc:
        raise VpnServiceError(str(exc)) from exc

    config_text = _build_client_config(
        client_private_key=client_private_key,
        allowed_ip=allowed_ip,
        dns=payload.dns,
        router_public_key=router_public_key,
        endpoint=endpoint,
    )
    qr_code_base64 = generate_qr_base64(config_text)

    peer = VPNPeer(
        router_id=router.id,
        peer_name=payload.username,
        vpn_type=VpnType.wireguard,
        public_key=client_public_key,
        allowed_ip=allowed_ip,
        endpoint=endpoint,
        dns=payload.dns,
        description=payload.description,
        status=VpnPeerStatus.configured,
        created_by_user_id=created_by_user_id,
    )
    db.add(peer)
    await db.commit()
    await db.refresh(peer)

    return WireguardPeerResult(
        peer=VPNPeerOut.model_validate(peer), config_text=config_text, qr_code_base64=qr_code_base64
    )


async def sync_vpn_peers(db: AsyncSession, router_id: int, live_peers: list[dict]) -> None:
    """Upsert VPNPeer rows (matched by router_id + peer_name + vpn_type) with
    live status/rx/tx/last_seen from RouterService.get_vpn()."""
    result = await db.execute(select(VPNPeer).where(VPNPeer.router_id == router_id))
    existing = {(p.peer_name, p.vpn_type.value): p for p in result.scalars().all()}

    for live in live_peers:
        key = (live["peer_name"], live["vpn_type"])
        peer = existing.get(key)
        last_seen = None
        if live.get("last_seen") and live["last_seen"] not in ("never",):
            last_seen = datetime.now(timezone.utc)

        if peer is None:
            peer = VPNPeer(
                router_id=router_id,
                peer_name=live["peer_name"],
                vpn_type=VpnType(live["vpn_type"]),
                public_key=live.get("public_key"),
            )
            db.add(peer)

        peer.allowed_ip = live.get("allowed_ip") or peer.allowed_ip
        peer.remote_address = live.get("remote_address")
        peer.rx_bytes = live.get("rx", 0)
        peer.tx_bytes = live.get("tx", 0)
        peer.status = VpnPeerStatus(live["status"]) if live.get("status") in VpnPeerStatus._value2member_map_ else VpnPeerStatus.unknown
        if last_seen:
            peer.last_seen = last_seen

    await db.commit()
