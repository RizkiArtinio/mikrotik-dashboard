# Deployment (Ubuntu Server + Docker)

## 1. Prerequisites

- Ubuntu Server 22.04 or 24.04, with a public IP or port-forwarded 80/443.
- A DNS A record pointing your domain (e.g. `dashboard.example.com`) at that IP.
- The target MikroTik router (RB4011iGS+ / RB750Gr3, RouterOS 7.x) reachable from this server:
  - RouterOS API port open (`8728` plaintext or `8729` API-SSL) — `/ip service` on the router.
  - SSH/SFTP port `22` open and enabled — backups are fetched via SFTP after being generated through the API (RouterOS's API cannot stream binary file contents directly).
  - ICMP allowed outbound from the router (for ISP ping monitoring) and from this server to the router.

## 2. Install Docker

```bash
sudo apt update && sudo apt install -y ca-certificates curl gnupg
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
newgrp docker
```

## 3. Get the code onto the server

```bash
git clone <your-repo-url> mikrotik-dashboard
cd mikrotik-dashboard
```

## 4. Configure environment

```bash
cp .env.example .env
nano .env
```

At minimum, set: `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, `FERNET_KEY`, `SEED_ADMIN_EMAIL`/`SEED_ADMIN_PASSWORD`, `DOMAIN`, `CERTBOT_EMAIL`. See [env-vars.md](env-vars.md) for the full list. You do **not** need to fill in the router credentials here if you'd rather add the router later through the UI (Admin → Routers) — either path stores the password Fernet-encrypted.

## 5. Start the stack

```bash
cd docker
docker compose --env-file ../.env up --build -d
```

This builds and starts `postgres`, `backend` (runs `alembic upgrade head` automatically before serving), and `frontend`. `nginx` will fail to start on the first run because no TLS certificate exists yet — that's expected, continue to the next step.

## 6. Bootstrap the first HTTPS certificate

```bash
./init-letsencrypt.sh
```

This creates a temporary self-signed cert so nginx can start, requests the real Let's Encrypt certificate via the HTTP-01 webroot challenge, then reloads nginx with it. Certificates auto-renew afterward via the `certbot` container (checks every 12h, renews within its 30-day window).

## 7. First login

Visit `https://<DOMAIN>` and log in with `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD`. Immediately:

1. Change the admin password (Admin → App Users, or via `PUT /users/{id}`).
2. Add your router under Admin → Routers (IP, username, password, API port). Use "Test" to verify connectivity before relying on it.
3. Set the router's ISP Gateway and WireGuard Endpoint fields if you plan to use ISP monitoring / the VPN generator.
4. Review Admin → Alert Settings and enable Telegram/Email in `.env` if you want notifications (requires `TELEGRAM_ENABLED=true` / `EMAIL_ENABLED=true` plus their respective credentials, then `docker compose --env-file ../.env up -d backend` to pick up the change).

## 8. Verifying it's working

- `docker compose --env-file ../.env ps` — all services should be `Up`/`healthy`.
- `docker compose --env-file ../.env logs -f backend` — should show the scheduler starting and successful poll cycles once a router is added.
- Dashboard page should show live CPU/memory/uptime within 5 seconds of loading, updating in place (WebSocket) — the connection badge in the top-right of Interfaces/Dashboard reads "Live" when the socket is connected, "Polling (fallback)" if it had to fall back to REST.

## 9. Updating

```bash
git pull
cd docker
docker compose --env-file ../.env up --build -d
```

Migrations run automatically on backend startup; no manual `alembic upgrade` step needed.

## 10. Backups of the dashboard's own database

The application backs up **router configs**, not itself. Separately back up the `pgdata` and `backups_data` Docker volumes (e.g. via `docker run --rm -v pgdata:/data -v $(pwd):/backup alpine tar czf /backup/pgdata.tar.gz /data`) as part of your normal server backup routine — this is outside the app's scope.
