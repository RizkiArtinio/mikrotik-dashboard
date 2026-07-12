from app.models.alert_rule import AlertType
from app.models.router import Router
from app.services.alert_evaluator import _conditions_for


def _router() -> Router:
    r = Router()
    r.id = 1
    r.name = "RB4011-Main"
    r.ip_address = "192.168.88.1"
    return r


def test_router_down_short_circuits_other_checks():
    conditions = _conditions_for(
        _router(),
        online=False,
        resources={"cpu_load": 99, "free_memory": 0, "total_memory": 100},
        vpn_peers=[{"peer_name": "alice", "status": "disconnected"}],
        isp_results=[{"target": "8.8.8.8", "label": "8.8.8.8", "status": "down"}],
        cpu_threshold=90,
        mem_threshold=90,
    )
    assert len(conditions[AlertType.router_down]) == 1
    assert conditions[AlertType.cpu_high] == []
    assert conditions[AlertType.vpn_down] == []


def test_cpu_and_memory_thresholds():
    conditions = _conditions_for(
        _router(),
        online=True,
        resources={"cpu_load": 95, "free_memory": 5, "total_memory": 100},
        vpn_peers=[],
        isp_results=[],
        cpu_threshold=90,
        mem_threshold=90,
    )
    assert len(conditions[AlertType.cpu_high]) == 1
    assert len(conditions[AlertType.mem_high]) == 1


def test_vpn_and_isp_down_detected():
    conditions = _conditions_for(
        _router(),
        online=True,
        resources=None,
        vpn_peers=[{"peer_name": "bob", "status": "disconnected"}, {"peer_name": "carol", "status": "connected"}],
        isp_results=[{"target": "1.1.1.1", "label": "1.1.1.1", "status": "down"}],
        cpu_threshold=90,
        mem_threshold=90,
    )
    assert len(conditions[AlertType.vpn_down]) == 1
    assert conditions[AlertType.vpn_down][0].target == "bob"
    assert len(conditions[AlertType.isp_down]) == 1
