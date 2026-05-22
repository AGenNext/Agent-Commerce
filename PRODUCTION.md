# Production Readiness Checklist

This project is suitable for local development and MVP testing, but production deployments must satisfy the controls below.

## Required environment

Set these values before running with `ENVIRONMENT=production`:

- `API_KEY`: strong user/API credential.
- `ADMIN_API_KEY`: separate strong admin credential.
- `JWT_SECRET`: random secret with at least 32 bytes of entropy.
- `SURREALDB_URL`: persistent SurrealDB endpoint. Do not use `mem://` in production.
- `SURREALDB_USER` and `SURREALDB_PASSWORD`: database credentials with least privilege.

## Deployment requirements

- Terminate TLS at a reverse proxy or load balancer.
- Store secrets in a secret manager.
- Run SurrealDB with persistent storage and authentication enabled.
- Configure health checks against `/health` and readiness checks against `/ready`.

## Known limitations

- Refresh tokens are stored in process memory.
- Rate limiting is process-local.
- Additional integration and load testing is recommended before large-scale production rollout.
