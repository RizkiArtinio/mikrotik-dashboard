# Architecture

## Overview

```
                     ┌─────────────┐
                     │   Browser    │
                     └──────┬──────┘
                            │ HTTPS (443)
                     ┌──────▼──────┐
                     │    nginx     │  reverse proxy + TLS termination
                     └───┬─────┬───┘
                 /api,/ws│     │/
                 ┌───────▼──┐ ┌▼────────┐
                 │  backend  │ │ frontend │  (static SPA build)
                 │  FastAPI  │ └─────────┘
                 └─┬───────┬─┘
                   │       │
          ┌────────▼─┐   ┌─▼──────────┐
          │ PostgreSQL│   │ RouterOS   │  RouterOS API (port 8728/8729)
          │           │   │ device(s)  │  + SFTP (port 22, for backups)
          └───────────┘   └────────────┘
```

## Backend layers

- **`app/api/routes/`** — REST endpoints. Every route (except `/auth/login`) requires a valid JWT; mutating/admin routes additionally require a role via `require_role(...)` (see [rbac.md](rbac.md)).
- **`app/services/`** — business logic. `router_service.py` is the single point of contact with RouterOS (`routeros-api`), used by every other service (`vpn_service`, `backup_service`, `firewall_service`, `dhcp_service`, `ppp_hotspot_service`, `isp_ping_service`, `dashboard_service`).
- **`app/scheduler/`** — APScheduler background jobs:
  - `poll_all_routers` (every `DASHBOARD_POLL_INTERVAL_SECONDS`, default 5s) — polls each active router, upserts `Interface`/`VPNPeer` rows, broadcasts over WebSocket, and runs alert evaluation on the same data (no duplicate router calls).
  - `snapshot_all_routers` (every `TRAFFIC_SNAPSHOT_INTERVAL_MINUTES`) — writes `TrafficHistory` rows used by the day/week/month bandwidth charts.
  - `run_daily_backups` (cron, default 02:00) — triggers `.backup` + `.rsc` generation and SFTP retrieval for every active router.
- **`app/websocket/`** — `ConnectionManager` tracks subscriber sockets per `"{channel}:{router_id}"` key (`dashboard` and `interfaces` channels are independent so a dashboard-only client never receives interface-tick traffic). Events are pushed as `{type, router_id, data, ts}`.
- **`app/models/` / `app/db/`** — SQLAlchemy 2 async models + Alembic migrations.

## Data flow: 5-second dashboard refresh

1. `jobs_poll_router.poll_all_routers` fires on the interval trigger.
2. For each active router, `dashboard_service.poll_and_build_snapshot` calls `RouterService.get_resources/get_health/get_interfaces/get_vpn` concurrently (each wrapped in `asyncio.to_thread` since `routeros-api` is synchronous).
3. Interface bps is **not** read directly from the router — RouterOS only exposes cumulative byte counters. The scheduler computes bps as `(new_bytes - previous_bytes) * 8 / elapsed_seconds`, comparing against the previous `Interface` row.
4. Updated rows are committed, then broadcast to WebSocket subscribers (`ws://<domain>/ws/dashboard/{router_id}` and `/ws/interfaces/{router_id}`).
5. The frontend's `useDashboardSocket`/`useInterfaceSocket` hooks hold the live connection and fall back to REST polling (`refetchInterval: 5000`) if the socket drops, so the UI degrades gracefully rather than freezing.

## Why RouterOS API only (no SNMP) in v1

The spec asks for interface/resource/health/VPN/firewall/DHCP data — all of which `routeros-api` already exposes without a second polling path. SNMP fields (`snmp_enabled`, `snmp_port`, `snmp_community_encrypted`) are reserved on the `Router` model for a future release but are not read anywhere in v1. This was a deliberate scope decision (see the implementation plan) to keep one connection path per router instead of two.

## Security

- Router passwords are Fernet-encrypted (`app/core/crypto.py`) before being written to `routers.password_encrypted`; the key lives in `FERNET_KEY` (never committed).
- App login uses JWT (`app/core/security.py`), bcrypt password hashing, and RBAC via FastAPI dependencies.
- WebSocket connections authenticate via a `?token=<jwt>` query parameter (browsers cannot set custom headers on WS handshakes).
