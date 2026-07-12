# MikroTik RouterOS v7 Monitoring & Management Dashboard

Enterprise monitoring and management dashboard for MikroTik RouterOS v7 devices (target hardware: RB4011iGS+ / RB750Gr3, RouterOS 7.16.2), architected to support multiple routers/sites from day one.

## Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2 (async), PostgreSQL, APScheduler, WebSocket, `routeros-api`
- **Frontend:** React 18, TypeScript, Material UI, Recharts, Axios, TanStack Query, Vite
- **Database:** PostgreSQL 16
- **Containers:** Docker Compose (frontend, backend, postgres, nginx, certbot)

## Project layout

```
backend/    FastAPI application (REST + WebSocket API, RouterOS integration, scheduler)
frontend/   React + TypeScript dashboard
database/   Schema documentation and optional manual seed scripts
docker/     docker-compose.yml, nginx reverse-proxy config, certbot config
docs/       Architecture, deployment, RBAC and environment variable reference
```

## Quick start (development)

```bash
cp .env.example .env   # fill in real values (see docs/env-vars.md)
cd docker
docker compose --env-file ../.env up --build -d
./init-letsencrypt.sh  # one-time: bootstrap the first HTTPS certificate
```

Frontend: https://<DOMAIN> (or http://localhost if running without certbot)
Backend API docs (Swagger): `/api/docs`

See [docs/deployment.md](docs/deployment.md) for full Ubuntu server deployment steps and [docs/env-vars.md](docs/env-vars.md) for every required environment variable.

## Security notes

- MikroTik router passwords are encrypted at rest (Fernet) before being stored in PostgreSQL.
- Application auth uses JWT with role-based access control (Super Admin / Network Engineer / Viewer).
- No credentials are committed to this repository — `.env` is gitignored, `.env.example` contains placeholders only.
