import pytest

from app.services.vpn_service import VpnServiceError, _parse_pool_ranges, find_available_ip


def test_parse_single_range():
    assert _parse_pool_ranges("172.30.30.110-172.30.30.112") == [
        (__import__("ipaddress").IPv4Address("172.30.30.110"), __import__("ipaddress").IPv4Address("172.30.30.112"))
    ]


def test_parse_multiple_ranges():
    ranges = _parse_pool_ranges("172.16.0.1-172.16.16.0,172.16.16.2-172.16.255.254")
    assert len(ranges) == 2


class FakeRouterService:
    def __init__(self, pools, wg_allowed=(), leases=(), addresses=()):
        self._pools = pools
        self._wg_allowed = wg_allowed
        self._leases = leases
        self._addresses = addresses

    def get_ip_pools(self):
        return self._pools

    def get_wireguard_peers(self):
        return [{"allowed_address": a} for a in self._wg_allowed]

    def get_dhcp_leases(self):
        return [{"ip_address": ip} for ip in self._leases]

    def get_ip_addresses(self):
        return [{"address": a} for a in self._addresses]


def test_find_available_ip_picks_first_free():
    service = FakeRouterService(pools=[{"name": "vpn-pool", "ranges": "172.30.30.110-172.30.30.112"}])
    assert find_available_ip(service, "vpn-pool") == "172.30.30.110/32"


def test_find_available_ip_skips_used_addresses():
    service = FakeRouterService(
        pools=[{"name": "vpn-pool", "ranges": "172.30.30.110-172.30.30.112"}],
        wg_allowed=["172.30.30.110/32"],
        leases=["172.30.30.111"],
    )
    assert find_available_ip(service, "vpn-pool") == "172.30.30.112/32"


def test_find_available_ip_exhausted_pool_raises():
    service = FakeRouterService(
        pools=[{"name": "vpn-pool", "ranges": "172.30.30.110-172.30.30.111"}],
        wg_allowed=["172.30.30.110/32", "172.30.30.111/32"],
    )
    with pytest.raises(VpnServiceError, match="exhausted"):
        find_available_ip(service, "vpn-pool")


def test_find_available_ip_unknown_pool_raises():
    service = FakeRouterService(pools=[{"name": "other-pool", "ranges": "10.0.0.1-10.0.0.2"}])
    with pytest.raises(VpnServiceError, match="not found"):
        find_available_ip(service, "vpn-pool")
