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

## Run locally with Docker Desktop

Requires Docker Desktop running. From the repo root:

```bash
docker compose up -d --build        # SurrealDB -> migrate (schema) -> API
docker compose ps                   # all services healthy/exited(migrate)=0
curl -s localhost:8080/health       # {"status":"healthy"}
curl -s localhost:8080/ready        # {"status":"ready","db":"connected"}
docker compose logs -f agent-api    # follow API logs
docker compose down                 # stop (add -v to wipe the DB volume)
```

With OpenFGA authorization:

```bash
docker compose -f docker-compose.yml -f docker-compose.openfga.yml up -d --build
docker compose logs openfga-model-load   # copy the printed store & model id
```

## Deploy to production (compose)

```bash
# Provide secrets via the environment or an .env file (never commit real values):
#   SURREALDB_USER, SURREALDB_PASSWORD, API_KEY, ADMIN_API_KEY, JWT_SECRET
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

The production override sets `ENVIRONMENT=production` (the API refuses weak
secrets and `mem://`), keeps the database off public ports, adds restart
policies and resource limits, and sets `OPENFGA_DEFAULT_ALLOW=false` so the
authorization gate **fails closed**. Migrations run automatically via the
one-shot `migrate` service; on Kubernetes the same step runs as an
init-container (`k8s/deployment.yaml`).

## Known limitations

- Refresh tokens are stored in process memory.
- Rate limiting is process-local.
- Additional integration and load testing is recommended before large-scale production rollout.
