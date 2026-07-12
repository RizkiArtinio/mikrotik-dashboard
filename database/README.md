# Database

PostgreSQL 16. The actual schema is defined by SQLAlchemy models in `backend/app/models/` and versioned by Alembic migrations in `backend/alembic/versions/` — that is the source of truth, not this directory.

Migrations run automatically when the `backend` container starts (`alembic upgrade head` in `docker-entrypoint.sh`). To run them manually:

```bash
cd backend
alembic upgrade head        # apply all pending migrations
alembic revision --autogenerate -m "description"   # generate a new migration after changing models
```

## Core tables

| Table | Purpose |
|---|---|
| `routers` | Registered MikroTik devices (multi-router/multi-site). Password stored Fernet-encrypted. |
| `interfaces` | Latest polled snapshot per router interface (upserted every 5s poll). |
| `vpn_peers` | WireGuard / L2TP / SSTP / OpenVPN / IPsec peer status, unified across VPN types. |
| `traffic_history` | Time-series RX/TX per interface, written periodically — backs the day/week/month bandwidth charts. |
| `backups` | Metadata for `.backup`/`.rsc` files retrieved from routers. |
| `users` | Application login accounts (Super Admin / Network Engineer / Viewer) — distinct from router PPP/Hotspot users, which are read live from the router and not persisted. |
| `alert_rules` | Threshold + cooldown configuration per alert type, editable via Admin → Alert Settings. |
| `notification_logs` | One row per sent notification; also the source of truth for cooldown/dedup logic. |

See [../docs/architecture.md](../docs/architecture.md) for how these tables are populated by the scheduler.
