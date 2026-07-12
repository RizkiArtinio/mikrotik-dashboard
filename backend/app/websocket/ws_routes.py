import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import get_current_user_ws
from app.db.session import AsyncSessionLocal
from app.websocket.connection_manager import connection_manager

logger = logging.getLogger(__name__)
router = APIRouter()


async def _authenticate(websocket: WebSocket) -> bool:
    token = websocket.query_params.get("token")
    async with AsyncSessionLocal() as db:
        user = await get_current_user_ws(token, db)
    if user is None:
        await websocket.close(code=4401)
        return False
    return True


@router.websocket("/ws/dashboard/{router_id}")
async def ws_dashboard(websocket: WebSocket, router_id: int) -> None:
    if not await _authenticate(websocket):
        return

    await connection_manager.connect("dashboard", router_id, websocket)
    try:
        while True:
            # Client doesn't need to send anything; we just keep the socket
            # alive and let broadcast() push data. recv() blocks until the
            # client disconnects or sends a (ignored) keepalive ping.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect("dashboard", router_id, websocket)


@router.websocket("/ws/interfaces/{router_id}")
async def ws_interfaces(websocket: WebSocket, router_id: int) -> None:
    if not await _authenticate(websocket):
        return

    await connection_manager.connect("interfaces", router_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect("interfaces", router_id, websocket)
