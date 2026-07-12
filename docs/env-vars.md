# Environment Variables Reference

Copy `.env.example` to `.env` at the project root and fill in real values. `.env` is gitignored — never commit it.

## Database

| Variable | Description |
|---|---|
| `POSTGRES_HOST` / `POSTGRES_PORT` / `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Used by the `postgres` container and to build `DATABASE_URL`. |
| `DATABASE_URL` | Full async SQLAlchemy URL, e.g. `postgresql+asyncpg://user:pass@postgres:5432/db`. Must match the components above when running under Docker Compose (host = service name `postgres`). |

## Auth / Security

| Variable | Description |
|---|---|
| `JWT_SECRET_KEY` | Random secret for signing JWTs. Generate with `openssl rand -hex 32`. |
| `JWT_ALGORITHM` | Default `HS256`. |
| `JWT_EXPIRE_MINUTES` | Access token lifetime. |
| `FERNET_KEY` | Encrypts router passwords at rest. Generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. **Losing this key makes all stored router passwords unrecoverable — back it up separately from the database.** |
| `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD` | First Super Admin account, created on first backend boot if no users exist. Change the password after first login. |

## Router (optional seed)

| Variable | Description |
|---|---|
| `SEED_DEFAULT_ROUTER` | `true` to auto-create a router row from the variables below on first boot. Leave `false` and add the router via the UI (Admin → Routers) instead if you'd rather not put real credentials in `.env` at all — the UI path encrypts and stores them the same way. |
| `DEFAULT_ROUTER_NAME` / `DEFAULT_ROUTER_IP` / `DEFAULT_ROUTER_API_PORT` / `DEFAULT_ROUTER_USERNAME` / `DEFAULT_ROUTER_PASSWORD` | Your RB4011iGS+ (or other RouterOS 7 device) connection details. API port is `8728` (plaintext) or `8729` (API-SSL) by default on RouterOS. |

## SNMP (reserved, unused in v1)

| Variable | Description |
|---|---|
| `SNMP_ENABLED` / `SNMP_COMMUNITY` | Not read by any code path yet — reserved for a future SNMP polling option alongside the RouterOS API path. |

## Polling / Scheduler

| Variable | Description |
|---|---|
| `DASHBOARD_POLL_INTERVAL_SECONDS` | Router poll + WebSocket broadcast cadence. Default `5`. |
| `TRAFFIC_SNAPSHOT_INTERVAL_MINUTES` | How often a `TrafficHistory` row is written per interface (feeds the bandwidth charts). |
| `BACKUP_DAILY_HOUR` / `BACKUP_DAILY_MINUTE` | Time of day (UTC, server clock) the daily backup job runs. |
| `ALERT_COOLDOWN_MINUTES_DEFAULT` | Default cooldown seeded into `alert_rules`; editable per-rule afterward in Admin → Alert Settings. |
| `CPU_ALERT_THRESHOLD` / `MEM_ALERT_THRESHOLD` | Percentage thresholds for the `cpu_high` / `mem_high` alerts. |
| `ISP_PING_TARGETS` | Comma-separated ping targets, default `8.8.8.8,1.1.1.1`. Each router's `isp_gateway` field (set per-router in Admin → Routers) is pinged in addition to these. |

## Telegram

| Variable | Description |
|---|---|
| `TELEGRAM_ENABLED` | Must be `true` for Telegram alerts to send. |
| `TELEGRAM_BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) — `/newbot`, copy the token. |
| `TELEGRAM_CHAT_ID` | The chat/group/channel ID to post alerts to. Message your bot once, then check `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your chat ID. |

## Email / SMTP

| Variable | Description |
|---|---|
| `EMAIL_ENABLED` | Must be `true` for email alerts to send. |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD` / `SMTP_FROM_ADDRESS` / `SMTP_USE_TLS` | Standard SMTP relay config. For Gmail, use an [App Password](https://myaccount.google.com/apppasswords), not your normal password. |
| `ALERT_EMAIL_RECIPIENTS` | Comma-separated list of recipient addresses. |

## Backups

| Variable | Description |
|---|---|
| `BACKUP_STORAGE_DIR` | Path inside the backend container where `.backup`/`.rsc` files are written (mounted to the `backups_data` volume). Leave as `/app/backups`. |

## Domain / TLS

| Variable | Description |
|---|---|
| `DOMAIN` | Public hostname the Ubuntu server is reachable at — used by nginx's server block and by `certbot` to request the certificate. |
| `CERTBOT_EMAIL` | Contact address for Let's Encrypt expiry notices. |

## Frontend (build-time)

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Default `/api` — nginx proxies this to the backend. Only change if you're not using the provided nginx config. |
| `VITE_WS_BASE_URL` | Default `/ws` — same idea for WebSocket traffic. |

## CORS

| Variable | Description |
|---|---|
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins allowed to call the API directly (mostly relevant for local `vite dev` against a remote backend). The production nginx setup serves frontend and backend from the same origin, so this matters less there. |
