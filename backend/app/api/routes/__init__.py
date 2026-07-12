from fastapi import APIRouter, Depends

from app.core.security import get_current_user

from . import (
    alerts,
    auth,
    backups,
    dashboard,
    dhcp,
    firewall,
    interfaces,
    isp,
    ppp_hotspot_users,
    resources,
    routers,
    traffic_history,
    users,
    vpn,
    vpn_generator,
)

api_router = APIRouter(prefix="/api")

# Auth endpoints are unauthenticated (login) or self-service (me).
api_router.include_router(auth.router)

# Everything else requires a valid JWT; per-route RBAC is layered on top via
# `require_role(...)` dependencies where mutation/admin access is needed.
_protected_dependency = Depends(get_current_user)
for module in (
    users,
    routers,
    dashboard,
    interfaces,
    traffic_history,
    resources,
    vpn,
    vpn_generator,
    backups,
    isp,
    firewall,
    dhcp,
    ppp_hotspot_users,
    alerts,
):
    api_router.include_router(module.router, dependencies=[_protected_dependency])

__all__ = ["api_router"]
