"""Synchronous wrapper around `routeros-api`, one instance per Router row.

All methods are synchronous because the underlying `routeros-api` library is
synchronous. Async callers (API routes, scheduler jobs) must invoke these via
`asyncio.to_thread(...)`.
"""

import logging

from routeros_api.exceptions import RouterOsApiCommunicationError

from app.models.router import Router
from app.services.router_connection_pool import connection_pool

logger = logging.getLogger(__name__)


class RouterConnectionError(Exception):
    """Raised when the router cannot be reached at all."""


class RouterCommandError(Exception):
    """Raised when the router was reachable but rejected/errored on a command."""


class RouterService:
    def __init__(self, router: Router) -> None:
        self.router = router

    def connect(self):
        try:
            return connection_pool.get_api(self.router)
        except ConnectionError as exc:
            raise RouterConnectionError(str(exc)) from exc

    def _resource(self, path: str):
        api = self.connect()
        return api.get_resource(path)

    def _safe_get(self, path: str, **query) -> list[dict]:
        # Held for connect + get: the pooled connection's socket is shared
        # across every call site for this router, and routeros-api's
        # send/receive protocol is not safe for concurrent multi-threaded
        # use of the same socket (see RouterConnectionPool.get_io_lock).
        with connection_pool.get_io_lock(self.router.id):
            try:
                resource = self._resource(path)
                return resource.get(**query) if query else resource.get()
            except RouterOsApiCommunicationError as exc:
                raise RouterCommandError(f"Command failed on {path}: {exc}") from exc

    # ------------------------------------------------------------------
    # Required RouterService methods
    # ------------------------------------------------------------------

    # RouterOS reports short type codes on /interface print (confirmed
    # against a real RB4011: WireGuard interfaces come back as "wg", not
    # "wireguard"). Normalize to the names used throughout this app so type
    # comparisons (e.g. vpn_service picking a WireGuard interface) work
    # regardless of which short code RouterOS happens to use.
    _INTERFACE_TYPE_ALIASES = {"wg": "wireguard"}

    def get_interfaces(self) -> list[dict]:
        """Raw interface counters from /interface print. bps is NOT computed
        here — the scheduler derives it from the delta between consecutive
        polls (see app/scheduler/jobs_poll_router.py)."""
        rows = self._safe_get("/interface")
        return [
            {
                "name": r.get("name"),
                "type": self._INTERFACE_TYPE_ALIASES.get(
                    r.get("type", "ether"), r.get("type", "ether")
                ),
                "running": r.get("running") == "true",
                "disabled": r.get("disabled") == "true",
                "rx_bytes": int(r.get("rx-byte", 0) or 0),
                "tx_bytes": int(r.get("tx-byte", 0) or 0),
                "rx_packets": int(r.get("rx-packet", 0) or 0),
                "tx_packets": int(r.get("tx-packet", 0) or 0),
            }
            for r in rows
        ]

    def get_resources(self) -> dict:
        rows = self._safe_get("/system/resource")
        r = rows[0] if rows else {}
        return {
            "uptime": r.get("uptime"),
            "version": r.get("version"),
            "cpu_load": float(r.get("cpu-load", 0) or 0),
            "cpu_count": int(r.get("cpu-count", 0) or 0),
            "free_memory": int(r.get("free-memory", 0) or 0),
            "total_memory": int(r.get("total-memory", 0) or 0),
            "free_hdd_space": int(r.get("free-hdd-space", 0) or 0),
            "total_hdd_space": int(r.get("total-hdd-space", 0) or 0),
            "board_name": r.get("board-name"),
            "architecture_name": r.get("architecture-name"),
            "platform": r.get("platform"),
        }

    def get_health(self) -> dict:
        rows = self._safe_get("/system/health")
        # RouterOS 7 returns health as a list of {name, value, type} rows on
        # some boards and flat key/value on others — normalize both shapes.
        if rows and "name" in rows[0]:
            merged = {row.get("name"): row.get("value") for row in rows}
        else:
            merged = rows[0] if rows else {}

        def _num(key: str) -> float | None:
            val = merged.get(key)
            try:
                return float(val) if val is not None else None
            except (TypeError, ValueError):
                return None

        return {
            "voltage": _num("voltage"),
            "temperature": _num("temperature"),
            "cpu_temperature": _num("cpu-temperature"),
        }

    def get_routes(self) -> list[dict]:
        return self._safe_get("/ip/route")

    def get_firewall(self) -> list[dict]:
        rows = self._safe_get("/ip/firewall/filter")
        return [
            {
                "chain": r.get("chain"),
                "action": r.get("action"),
                "comment": r.get("comment"),
                "bytes": int(r.get("bytes", 0) or 0),
                "packets": int(r.get("packets", 0) or 0),
            }
            for r in rows
        ]

    def get_nat(self) -> list[dict]:
        rows = self._safe_get("/ip/firewall/nat")
        return [
            {
                "chain": r.get("chain"),
                "action": r.get("action"),
                "comment": r.get("comment"),
                "bytes": int(r.get("bytes", 0) or 0),
                "packets": int(r.get("packets", 0) or 0),
            }
            for r in rows
        ]

    def get_dhcp_leases(self) -> list[dict]:
        rows = self._safe_get("/ip/dhcp-server/lease")
        return [
            {
                "hostname": r.get("host-name"),
                "mac_address": r.get("mac-address"),
                "ip_address": r.get("address"),
                "status": r.get("status"),
                "expires_after": r.get("expires-after"),
            }
            for r in rows
        ]

    def get_ip_pools(self) -> list[dict]:
        rows = self._safe_get("/ip/pool")
        return [{"name": r.get("name"), "ranges": r.get("ranges", "")} for r in rows]

    def get_ip_addresses(self) -> list[dict]:
        rows = self._safe_get("/ip/address")
        return [{"address": r.get("address"), "interface": r.get("interface")} for r in rows]

    def get_ppp_active(self) -> list[dict]:
        rows = self._safe_get("/ppp/active")
        return [
            {
                "username": r.get("name"),
                "service": r.get("service"),
                "caller_id": r.get("caller-id"),
                "address": r.get("address"),
                "login_time": r.get("uptime"),
            }
            for r in rows
        ]

    def get_ppp_secrets(self) -> list[dict]:
        rows = self._safe_get("/ppp/secret")
        return [{"name": r.get("name"), "service": r.get("service")} for r in rows]

    def create_ppp_secret(
        self, username: str, password: str, service: str = "l2tp", profile: str = "default", comment: str | None = None
    ) -> None:
        params = {"name": username, "password": password, "service": service, "profile": profile}
        if comment:
            params["comment"] = comment
        with connection_pool.get_io_lock(self.router.id):
            try:
                self._resource("/ppp/secret").add(**params)
            except RouterOsApiCommunicationError as exc:
                raise RouterCommandError(f"Failed to create PPP secret: {exc}") from exc

    def get_l2tp_server_ipsec_secret(self) -> str | None:
        rows = self._safe_get("/interface/l2tp-server/server")
        if not rows:
            return None
        return rows[0].get("ipsec-secret")

    def get_ovpn_server_config(self) -> dict:
        rows = self._safe_get("/interface/ovpn-server/server")
        r = rows[0] if rows else {}
        return {
            "enabled": r.get("enabled") == "true",
            "port": int(r.get("port", 1194) or 1194),
            "protocol": r.get("protocol", "tcp"),
            "cipher": (r.get("cipher") or "aes256-cbc").split(",")[0],
            "auth": (r.get("auth") or "sha256").split(",")[0],
        }

    def export_certificate_pem(self, cert_name: str) -> str:
        """Triggers a PEM export of `cert_name` to the router's local
        filesystem as `cert_export_<cert_name>.crt`. Caller is responsible
        for fetching the actual file contents via SFTP (sftp_client.py) —
        the RouterOS API itself has no "read file contents" command."""
        with connection_pool.get_io_lock(self.router.id):
            try:
                self._resource("/certificate").call("export-certificate", {"numbers": cert_name, "type": "pem"})
            except RouterOsApiCommunicationError as exc:
                raise RouterCommandError(f"Failed to export certificate {cert_name}: {exc}") from exc
        return f"cert_export_{cert_name}.crt"

    def get_hotspot_active(self) -> list[dict]:
        try:
            rows = self._safe_get("/ip/hotspot/active")
        except RouterCommandError:
            return []
        return [
            {
                "username": r.get("user"),
                "address": r.get("address"),
                "mac_address": r.get("mac-address"),
                "login_time": r.get("login-time"),
                "uptime": r.get("uptime"),
                "bytes_in": int(r.get("bytes-in", 0) or 0),
                "bytes_out": int(r.get("bytes-out", 0) or 0),
            }
            for r in rows
        ]

    def get_wireguard_peers(self, interface: str | None = None) -> list[dict]:
        rows = self._safe_get("/interface/wireguard/peers")
        peers = []
        for r in rows:
            if interface and r.get("interface") != interface:
                continue
            peers.append(
                {
                    "peer_name": r.get("comment") or r.get("public-key", "")[:16],
                    "public_key": r.get("public-key"),
                    "allowed_address": r.get("allowed-address"),
                    "endpoint": r.get("current-endpoint-address"),
                    "rx": int(r.get("rx", 0) or 0),
                    "tx": int(r.get("tx", 0) or 0),
                    "last_handshake": r.get("last-handshake"),
                    "interface": r.get("interface"),
                }
            )
        return peers

    def get_wireguard_interface_public_key(self, interface: str) -> str | None:
        rows = self._safe_get("/interface/wireguard")
        for r in rows:
            if r.get("name") == interface:
                return r.get("public-key")
        return None

    def get_ipsec_active_peers(self) -> list[dict]:
        try:
            return self._safe_get("/ip/ipsec/active-peers")
        except RouterCommandError:
            return []

    def get_vpn(self) -> list[dict]:
        """Unified view across WireGuard / L2TP / SSTP / OpenVPN (PPP-based) / IPsec."""
        results: list[dict] = []

        for peer in self.get_wireguard_peers():
            results.append(
                {
                    "vpn_type": "wireguard",
                    "peer_name": peer["peer_name"],
                    "public_key": peer["public_key"],
                    "allowed_ip": peer["allowed_address"],
                    "remote_address": peer["endpoint"],
                    "rx": peer["rx"],
                    "tx": peer["tx"],
                    "last_seen": peer["last_handshake"],
                    "status": "connected" if peer["last_handshake"] not in (None, "never") else "disconnected",
                }
            )

        service_to_vpn_type = {"l2tp": "l2tp", "sstp": "sstp", "ovpn": "openvpn", "pptp": "l2tp"}
        for active in self.get_ppp_active():
            vpn_type = service_to_vpn_type.get(active.get("service"))
            if vpn_type is None:
                continue
            results.append(
                {
                    "vpn_type": vpn_type,
                    "peer_name": active["username"],
                    "public_key": None,
                    "allowed_ip": active.get("address"),
                    "remote_address": active.get("caller_id"),
                    "rx": 0,
                    "tx": 0,
                    "last_seen": active.get("login_time"),
                    "status": "connected",
                }
            )

        for peer in self.get_ipsec_active_peers():
            results.append(
                {
                    "vpn_type": "ipsec",
                    "peer_name": peer.get("id", peer.get("remote-address", "ipsec-peer")),
                    "public_key": None,
                    "allowed_ip": None,
                    "remote_address": peer.get("remote-address"),
                    "rx": 0,
                    "tx": 0,
                    "last_seen": peer.get("uptime"),
                    "status": "connected" if peer.get("state") == "established" else "unknown",
                }
            )

        return results

    def create_wireguard_peer(
        self, interface: str, public_key: str, allowed_address: str, comment: str | None = None
    ) -> dict:
        params = {"interface": interface, "public-key": public_key, "allowed-address": allowed_address}
        if comment:
            params["comment"] = comment
        with connection_pool.get_io_lock(self.router.id):
            try:
                self._resource("/interface/wireguard/peers").add(**params)
            except RouterOsApiCommunicationError as exc:
                raise RouterCommandError(f"Failed to create WireGuard peer: {exc}") from exc
        return params

    def create_backup(self, name: str) -> dict:
        """Triggers both a binary .backup and a plaintext .rsc export on the
        router filesystem. Returns the filenames — actual download from the
        router (SFTP) is handled by backup_service.py."""
        with connection_pool.get_io_lock(self.router.id):
            try:
                self._resource("/system/backup").call("save", {"name": name})
                # "/export" is a top-level command, not a CRUD resource — the
                # command word is sent as "export" against the root path "/",
                # same pattern as `/system reboot` (see connect()/get_api()
                # callers using RouterService._resource("/system").call("reboot", ...)).
                # Calling _resource("/export").call("export", ...) instead
                # sends the invalid path "/export/export" ("no such command").
                self._resource("/").call("export", {"file": name})
            except RouterOsApiCommunicationError as exc:
                raise RouterCommandError(f"Backup command failed: {exc}") from exc
        return {"backup_file": f"{name}.backup", "rsc_file": f"{name}.rsc"}
