# Agent-Commerce 🛒🤖

AI-powered e-commerce agents built with Universal Commerce Protocol (UCP), Agents Payment Protocol(AP2), A2A Protocol.

![Tests](https://img.shields.io/badge/tests-57%20passed-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-Apache2-orange)

## Features

- **UCP Commerce Agent** - AI agent with 40+ commerce skills
- **Store Manager** - WooCommerce, Shopify, Mercur integrations
- **Payment Protocols** - 8 providers: AP2, x402, Stripe, PayPal, Mastercard, Open Banking, MPP, Shopify
- **Marketplace Manager** - Vendors, commissions, payouts, disputes
- **Site Admin** - Users, roles, API keys, webhooks
- **SurrealDB Layer** - Centralized data with CRUD, relations, search
- **FastAPI Runtime** - JWT auth, rate limiting, readiness checks

## Installation

```bash
git clone https://github.com/AGenNext/Agent-Commerce.git
cd Agent-Commerce
pip install -r requirements.txt
```

## Local Development

```bash
cp .env.example .env
docker compose up -d
```

Endpoints:

- API: http://localhost:8080
- Health: http://localhost:8080/health
- Readiness: http://localhost:8080/ready
- Docs: http://localhost:8080/docs

## Authentication

Supported authentication methods:

- API keys
- Admin API keys
- JWT bearer tokens
- Refresh tokens

Example request:

```bash
curl -H "X-API-Key: local-dev-api-key" http://localhost:8080/api/providers
```

## Production Deployment

Required environment variables:

```env
ENVIRONMENT=production
API_KEY=<high-entropy-secret>
ADMIN_API_KEY=<high-entropy-secret>
JWT_SECRET=<high-entropy-secret>
SURREALDB_URL=<persistent-db-url>
SURREALDB_USER=<db-user>
SURREALDB_PASSWORD=<db-password>
```

Production recommendations:

- Use a persistent external SurrealDB deployment
- Put the API behind TLS/reverse proxy infrastructure
- Replace in-memory rate limiting with Redis or gateway limits
- Persist refresh tokens outside process memory
- Add centralized observability and tracing
- Rotate secrets regularly
- Use orchestration such as Kubernetes or ECS

## Docker

```bash
docker build -t agent-commerce .
docker run -p 8000:8000 --env-file .env agent-commerce
```

## CI/CD

GitHub Actions validates:

- Ruff linting
- MyPy type checks
- Pytest execution
- Health endpoint smoke tests
- Docker image build

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

## License

Apache 2.0 - See LICENSE file

---

Built with 💚 for autonomous commerce
