# API Reference

The backend generates a full interactive OpenAPI/Swagger UI — that is the source of truth for request/response shapes, not this file.

- Swagger UI: `https://<domain>/api/docs`
- Raw OpenAPI schema: `https://<domain>/api/openapi.json`

## Auth

All endpoints except `POST /api/auth/login` require `Authorization: Bearer <token>`. Obtain a token via:

```bash
curl -X POST https://<domain>/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "..."}'
```

WebSocket endpoints (`/ws/dashboard/{router_id}`, `/ws/interfaces/{router_id}`) authenticate via a `token` query parameter instead of a header, since browsers cannot set custom headers during the WebSocket handshake:

```
wss://<domain>/ws/dashboard/1?token=<jwt>
```

See [rbac.md](rbac.md) for which roles can call which endpoints.
