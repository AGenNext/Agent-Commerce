# Deploy Foundation Agent-Commerce Protocol Service

This service exposes the Foundation Agent-Commerce Protocol Profile as a small HTTP validator API.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/profile` | Markdown protocol profile |
| GET | `/schema` | JSON Schema profile |
| GET | `/examples` | Valid example payloads |
| POST | `/validate` | Validate a protocol payload |

## Docker

```bash
docker build -f Dockerfile.protocol -t agent-commerce-protocol:local .
docker run --rm -p 8080:8080 agent-commerce-protocol:local
```

Check health:

```bash
curl http://localhost:8080/health
```

## Docker Compose

```bash
docker compose -f docker-compose.protocol.yml up --build
```

## Kubernetes

Apply the manifests:

```bash
kubectl apply -f k8s/protocol-service.yaml
kubectl rollout status deployment/agent-commerce-protocol
kubectl port-forward svc/agent-commerce-protocol 8080:8080
```

Check:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/schema
```

## Validate a UCP Payload

```bash
curl -X POST http://localhost:8080/validate \
  -H 'Content-Type: application/json' \
  -d '{
    "payload": {
      "ucp_version": "0.1-profile",
      "type": "commerce.action.request",
      "action": "product.create",
      "actor": {"type": "agent", "id": "agent_store_helper"},
      "resource": {"type": "product"},
      "input": {"name": "Notebook", "price": 99, "currency": "INR", "stock": 50},
      "trace_id": "trace_001"
    }
  }'
```

Expected response:

```json
{
  "valid": true,
  "schema_id": "https://github.com/AGenNext/Agent-Commerce/schemas/foundation-agent-commerce-protocol-profile.schema.json",
  "errors": []
}
```

## Build and Publish Image

The GitHub workflow builds the protocol service container. On `main`, it can publish to GHCR as:

```text
ghcr.io/agennext/agent-commerce-protocol:latest
```

## Production Readiness Notes

Before using this for real payment execution, add:

- API authentication
- signed AP2 mandate verification
- nonce and idempotency persistence
- immutable audit logs
- rate limiting
- TLS ingress
- provider-specific payment adapters
- SBOM and image signing
