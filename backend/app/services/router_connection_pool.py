import logging
import threading

import routeros_api
from routeros_api.exceptions import RouterOsApiConnectionError

from app.core.crypto import decrypt_secret
from app.models.router import Router

logger = logging.getLogger(__name__)


class RouterConnectionPool:
    """Keeps one live RouterOsApiPool per router_id so the 5s poll cycle
    reuses a TCP connection instead of reconnecting every tick.
    `routeros-api` is synchronous — callers must run pool methods via
    asyncio.to_thread from async code.
    """

    def __init__(self) -> None:
        self._pools: dict[int, routeros_api.RouterOsApiPool] = {}
        self._lock = threading.Lock()

    def get_api(self, router: Router) -> routeros_api.api.RouterOsApi:
        with self._lock:
            pool = self._pools.get(router.id)
            if pool is not None:
                try:
                    return pool.get_api()
                except Exception:
                    logger.warning("Stale connection for router %s, reconnecting", router.id)
                    self._drop(router.id)

            try:
                pool = routeros_api.RouterOsApiPool(
                    router.ip_address,
                    username=router.username,
                    password=decrypt_secret(router.password_encrypted),
                    port=router.api_port,
                    use_ssl=router.use_ssl,
                    ssl_verify=False,
                    ssl_verify_hostname=False,
                    plaintext_login=True,
                )
                # Default is 15s, longer than the 5s poll interval — an
                # unreachable router would then stall the whole poll cycle
                # long enough for the next tick to be skipped (see
                # jobs_poll_router.py, which also polls routers concurrently
                # so one slow/down router can't delay the others).
                pool.socket_timeout = 5.0
                api = pool.get_api()
            except RouterOsApiConnectionError as exc:
                raise ConnectionError(f"Could not connect to router {router.id} ({router.ip_address})") from exc

            self._pools[router.id] = pool
            return api

    def _drop(self, router_id: int) -> None:
        pool = self._pools.pop(router_id, None)
        if pool is not None:
            try:
                pool.disconnect()
            except Exception:
                pass

    def invalidate(self, router_id: int) -> None:
        with self._lock:
            self._drop(router_id)

    def disconnect_all(self) -> None:
        with self._lock:
            for router_id in list(self._pools):
                self._drop(router_id)


connection_pool = RouterConnectionPool()
