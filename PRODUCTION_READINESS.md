# Production Readiness Checklist

## Security
- [ ] Replace API_KEY with a strong secret
- [ ] Enable HTTPS behind a reverse proxy
- [ ] Add authentication and role-based access control
- [ ] Rotate payment provider secrets

## Reliability
- [ ] Run CI on every PR
- [ ] Add monitoring and alerting
- [ ] Back up SurrealDB
- [ ] Configure rate limiting

## Operations
- [ ] Use a managed database or HA deployment
- [ ] Pin dependencies with a lock file
- [ ] Run vulnerability scans
- [ ] Set resource limits in deployment

## Application
- [ ] Replace dict payloads with Pydantic models
- [ ] Parameterize database queries
- [ ] Add structured logging
- [ ] Add webhook signature verification
