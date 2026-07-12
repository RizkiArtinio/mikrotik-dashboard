import asyncio
import logging

from icmplib import async_ping

from app.core.config import settings
from app.models.router import Router

logger = logging.getLogger(__name__)


async def _ping_target(target: str, label: str) -> dict:
    try:
        host = await async_ping(target, count=4, timeout=1, privileged=False)
        return {
            "target": target,
            "label": label,
            "latency_ms": round(host.avg_rtt, 2) if host.packets_received else None,
            "packet_loss_percent": round(host.packet_loss * 100, 1),
            "status": "up" if host.is_alive else "down",
        }
    except Exception as exc:
        logger.warning("Ping to %s (%s) failed: %s", target, label, exc)
        return {"target": target, "label": label, "latency_ms": None, "packet_loss_percent": 100.0, "status": "down"}


async def check_isp_status(router: Router) -> list[dict]:
    targets = [(t, t) for t in settings.isp_ping_target_list]
    if router.isp_gateway:
        targets.append((router.isp_gateway, "ISP Gateway"))

    return await asyncio.gather(*(_ping_target(target, label) for target, label in targets))
