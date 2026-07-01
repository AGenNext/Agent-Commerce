# Agent-Commerce 🛒🤖

AI-powered e-commerce agents built with Universal Commerce Protocol (UCP), Agents Payment Protocol(AP2), A2A Protocol.

![Tests](https://img.shields.io/badge/tests-57%20passed-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-Apache2-orange)
![Docker](https://github.com/AGenNext/Agent-Commerce/actions/workflows/docker-publish.yml/badge.svg)

## Features

- **UCP Commerce Agent** - AI agent with 40+ commerce skills
- **Store Manager** - WooCommerce, Shopify, Mercur integrations
- **Payment Protocols** - 8 providers: AP2, x402, Stripe, PayPal, Mastercard, Open Banking, MPP, Shopify
- **Marketplace Manager** - Vendors, commissions, payouts, disputes
- **Site Admin** - Users, roles, API keys, webhooks
- **SurrealDB Layer** - Centralized data with CRUD, relations, search
- **FastAPI Runtime** - JWT auth, rate limiting, secure headers, health/readiness probes

## Quick Start

```bash
git clone https://github.com/AGenNext/Agent-Commerce.git
cd Agent-Commerce
pip install -r requirements.txt
python test_e2e.py
```

## Local Development

```bash
cp .env.example .env
docker compose up -d
```

Local endpoints:

- API: http://localhost:8080
- Health: http://localhost:8080/health
- Readiness: http://localhost:8080/ready
- OpenAPI docs: http://localhost:8080/docs

## Authentication

The API supports API-key auth, admin API-key auth, and JWT bearer tokens.

Example API-key request:

```bash
curl -H "X-API-Key: local-dev-api-key" http://localhost:8080/api/providers
```

For production, set strong values for `API_KEY`, `ADMIN_API_KEY`, and `JWT_SECRET`. Never commit real secrets.

## Docker

```bash
docker build -t agent-commerce .
docker run -p 8000:8000 --env-file .env agent-commerce
```

## Production Deployment

The repository publishes a container image to GitHub Container Registry on every push to `main`.

```bash
docker pull ghcr.io/agennext/agent-commerce:latest
docker run -p 8000:8000 --env-file .env ghcr.io/agennext/agent-commerce:latest
```

Required production variables:

```env
ENVIRONMENT=production
API_KEY=<high-entropy-secret>
ADMIN_API_KEY=<high-entropy-secret>
JWT_SECRET=<high-entropy-secret>
SURREALDB_URL=<persistent-db-url>
SURREALDB_USER=<db-user>
SURREALDB_PASSWORD=<db-password>
SURREALDB_NAMESPACE=ucp
SURREALDB_DATABASE=ecommerce
```

Production checklist:

- Use a persistent external SurrealDB deployment; do not use `mem://` in production.
- Terminate TLS at a reverse proxy or load balancer.
- Replace in-memory rate limiting with Redis or gateway-level limits for multi-replica deployments.
- Persist refresh/session tokens outside process memory.
- Add metrics, tracing, and centralized log aggregation.
- Rotate API keys and JWT secrets regularly.
- Verify payment providers against sandbox environments before accepting real payments.

## SDK

### Python SDK

```python
from agent_commerce import Client

async with Client(api_key="sk_...") as client:
    product = await client.products.create({"title": "Widget", "price": 29.99})
    order = await client.orders.create({"customer_id": "cust_1", "line_items": []})
    payment = await client.payments.create("stripe", 29.99, "USD")
```

### JavaScript SDK

```javascript
// Coming soon
```

## Payment Providers

| Provider | Description |
|----------|-------------|
| `ap2` | Google/FIDO Agent Payments |
| `x402` | Coinbase/Cloudflare stablecoin |
| `stripe` | OpenAI/Stripe checkout |
| `paypal` | PayPal agent payments |
| `mastercard` | Mastercard Agent Pay |
| `openbanking` | PSD2/SEPA |
| `mpp` | Stripe/Tempo Machine Payments |
| `shopify` | Shopify Catalog/Checkout |

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe |
| POST | `/api/store/products` | Create product |
| GET | `/api/store/products` | List products |
| POST | `/api/store/orders` | Create order |
| GET | `/api/store/dashboard` | Get dashboard |
| POST | `/api/payments/{provider}` | Create payment |
| GET | `/api/providers` | List providers |
| GET | `/api/admin/users` | List users |
| GET | `/api/admin/roles` | List roles |

## Test Results

```
Tests: 57/57 PASSED (100%)

SurrealDB Layer   10/10
Store Manager    10/10
Platform Factory  3/3
Site Admin       10/10
Payment Adapters 24/24
```

## Source URLs

- [UCP Protocol](https://ucp.dev)
- [A2A Protocol](https://a2a-protocol.org)
- [SurrealDB](https://surrealdb.com)
- [Stripe Agentic Commerce](https://stripe.com/in/guides/agentic-commerce)
- [Mercur](https://www.mercurjs.com)
- [Stacker](https://stackerbuild.io)

## License

Apache 2.0 - See LICENSE file

## Contributing

PRs welcome! Please read the contributing guidelines first.

---

Built with 💚 for autonomous commerce
