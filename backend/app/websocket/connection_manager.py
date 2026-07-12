import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Keys connections by "{channel}:{router_id}" (e.g. "dashboard:1",
    "interfaces:1") so the dashboard and interface WebSocket channels don't
    cross-broadcast to each other's subscribers."""

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}

    @staticmethod
    def _key(channel: str, router_id: int) -> str:
        return f"{channel}:{router_id}"

    async def connect(self, channel: str, router_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(self._key(channel, router_id), set()).add(websocket)

    def disconnect(self, channel: str, router_id: int, websocket: WebSocket) -> None:
        key = self._key(channel, router_id)
        sockets = self._connections.get(key)
        if sockets is None:
            return
        sockets.discard(websocket)
        if not sockets:
            self._connections.pop(key, None)

    async def broadcast(self, channel: str, router_id: int, payload: dict) -> None:
        sockets = self._connections.get(self._key(channel, router_id))
        if not sockets:
            return
        dead: list[WebSocket] = []
        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            sockets.discard(ws)


connection_manager = ConnectionManager()
