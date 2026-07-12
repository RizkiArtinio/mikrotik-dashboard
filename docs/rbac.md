# Role-Based Access Control

Three roles, enforced via `app/core/security.py::require_role(...)` dependencies on top of a valid JWT (every non-login route requires authentication regardless of role).

| Role | Intended for |
|---|---|
| `super_admin` | Full control — manage routers, manage app users, edit alert thresholds. |
| `network_engineer` | Day-to-day operations — create VPN peers, trigger backups, view everything. |
| `viewer` | Read-only dashboards. |

## Endpoint matrix

| Action | Viewer | Network Engineer | Super Admin |
|---|:---:|:---:|:---:|
| View dashboard / interfaces / bandwidth / VPN status / ISP / firewall / DHCP / PPP-hotspot users | ✅ | ✅ | ✅ |
| `POST /routers/{id}/vpn/wireguard-peer` (create VPN peer) | ❌ | ✅ | ✅ |
| `POST /routers/{id}/backups` (trigger backup) | ❌ | ✅ | ✅ |
| `GET /backups/{id}/download` | ✅ | ✅ | ✅ |
| `POST /routers/{id}/test-connection` | ❌ | ✅ | ✅ |
| Create / update / delete routers (`/routers`) | ❌ | ❌ | ✅ |
| Manage app users (`/users`) | ❌ | ❌ | ✅ |
| Edit alert rules (`PUT /alert-rules/{id}`) | ❌ | ❌ | ✅ |
| View notification log | ✅ | ✅ | ✅ |

The first `super_admin` account is seeded automatically on first backend boot from `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD` (see [env-vars.md](env-vars.md)) if no users exist yet — change that password immediately after first login via `PUT /users/{id}`.
