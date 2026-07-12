import asyncio
import logging

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.router import Router
from app.services import alert_evaluator
from app.services.dashboard_service import poll_and_build_snapshot
from app.services.isp_ping_service import check_isp_status
from app.websocket.connection_manager import connection_manager
from app.websocket.events import make_event

logger = logging.getLogger(__name__)


async def _poll_one_router(router_id: int) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Router).where(Router.id == router_id, Router.is_active.is_(True)))
        router = result.scalar_one_or_none()
        if router is None:
            return

        snapshot = await poll_and_build_snapshot(db, router)

        await connection_manager.broadcast(
            "dashboard", router.id, make_event("dashboard_update", router.id, snapshot.model_dump(mode="json"))
        )
        await connection_manager.broadcast(
            "interfaces",
            router.id,
            make_event(
                "interface_update",
                router.id,
                [i.model_dump(mode="json") for i in snapshot.interfaces],
            ),
        )

        isp_results = await check_isp_status(router) if snapshot.online else []

        try:
            await alert_evaluator.evaluate(
                db,
                router,
                online=snapshot.online,
                resources=snapshot.resources.model_dump() if snapshot.resources else None,
                vpn_peers=[p.model_dump() for p in snapshot.vpn_peers],
                isp_results=isp_results,
            )
        except Exception:
            logger.exception("Alert evaluation failed for router %s", router.id)


async def poll_all_routers() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Router.id).where(Router.is_active.is_(True)))
        router_ids = [row[0] for row in result.all()]

    # Concurrent, not sequential: each router gets its own DB session (see
    # _poll_one_router), so one slow/unreachable router can't delay polling
    # of the others within the same 5s tick.
    results = await asyncio.gather(
        *(_poll_one_router(router_id) for router_id in router_ids), return_exceptions=True
    )
    for router_id, result in zip(router_ids, results):
        if isinstance(result, Exception):
            logger.exception("Unhandled error polling router %s", router_id, exc_info=result)
