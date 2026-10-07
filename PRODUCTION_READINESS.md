# Production Readiness Checklist

## Security
- [x] API/admin keys + JWT required in production (weak values rejected at startup — `server.py`)
- [ ] Enable HTTPS behind a reverse proxy (deploy-time)
- [x] Authentication and role-based access control (API keys, SurrealDB row-level `PERMISSIONS`, OpenFGA ReBAC)
- [ ] Rotate payment provider secrets

## Reliability
- [x] Run CI on every PR (CodeQL + container publish workflows)
- [ ] Add monitoring and alerting
- [ ] Back up SurrealDB
- [x] Rate limiting (process-local; use Redis/gateway limits for multiple replicas)

## Operations
- [ ] Use a managed database or HA deployment
- [x] Pin dependencies (`requirements.txt`; a lock file is still recommended)
- [ ] Run vulnerability scans
- [x] Resource limits set (`k8s/deployment.yaml`, `docker-compose.prod.yml`)
- [x] Schema migrations applied automatically before serving (compose `migrate` service / k8s init-container, in dependency order)

## Application
- [x] Pydantic request models (`server.py`)
- [x] Parameterized database queries (`surrealdb_layer.py` uses bound params)
- [x] Structured JSON logging (`server.py`)
- [ ] Add webhook signature verification
- [ ] Expose the membership/identity ecosystem via HTTP endpoints (currently manager + SDK only)
