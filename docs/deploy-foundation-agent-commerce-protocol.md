# Deploy Foundation Agent-Commerce Protocol Service

This guide runs the Foundation Agent-Commerce Protocol Profile as a small HTTP service.

The service exposes:

- `GET /health`
- `GET /profile`
- `GET /schema`
- `GET /examples`
- `POST /validate`

## Local Docker Build

```bash
docker build -f Dockerfile.protocol -t agent-commerce-protocol:local .
docker run --rm -p 8080:8080 agent-commerce-protocol:local
```

Open:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/schema
curl http://localhost:8080/examples
```

## Docker Compose

```bash
docker compose -f docker-compose.protocol.yml up --build
```

## Validate a Payload

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
  "schema": "https://github.com/AGenNext/Agent-Commerce/schemas/foundation-agent-commerce-protocol-profile.schema.json",
  "errors": []
}
```

## Production Notes

For production deployment, add:

- signed AP2 mandate verification
- replay protection for `nonce` and idempotency keys
- persistent audit store
- TLS termination
- rate limits
- API key or workload identity
- OpenTelemetry traces
- signed container images
