import asyncio
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

    client_private_key, client_public_key = generate_keypair()

    try:
        await asyncio.to_thread(
            service.create_wireguard_peer,
            wg_interface_name,
            client_public_key,
            payload.allowed_ip,
            payload.description or payload.username,
        )
    except RouterCommandError as exc:
        raise VpnServiceError(str(exc)) from exc

    config_text = _build_client_config(
        client_private_key=client_private_key,
        allowed_ip=payload.allowed_ip,
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
        allowed_ip=payload.allowed_ip,
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
