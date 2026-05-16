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

## Quick Start

```python
# Install
pip install surrealdb aiohttp fastapi uvicorn

# Create product
from store_manager import StoreManager

store = StoreManager(config={})
product = await store.create_product({
    "title": "AI Widget",
    "price": 29.99
})
print(f"Created: {product['id']}")

# Process payment
from adapters import PaymentAdapterFactory

adapter = PaymentAdapterFactory.create("stripe")
payment = await adapter.create_payment(29.99, "USD")
print(f"Payment: {payment['id']}")
```

## Installation

```bash
# Clone
git clone https://github.com/AGenNext/Agent-Commerce.git
cd Agent-Commerce

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_e2e.py
```

## Docker

```bash
# Build
docker build -t agent-commerce .

# Run
docker run -p 8000:8000 agent-commerce
```

## API Server

```bash
python server.py
# Visit http://localhost:8000
```

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

## Project Structure

```
/workspace/project/
├── ucp_agent.py           # UCP Commerce Agent
├── store_manager.py       # Store Manager
├── site_admin.py        # Site Admin
├── vendor_agent.py      # Vendor Agent
├── marketplace_manager.py # Marketplace
├── surrealdb_layer.py   # SurrealDB layer
├── server.py            # FastAPI server
├── index.html          # Landing page
├── Dockerfile          # Container
├── adapters/           # 8 payment adapters
│   ├── ap2_adapter.py
│   ├── x402_adapter.py
│   ├── stripe_adapter.py
│   └── ...
└── sdk/
    ├── python/          # Python SDK
    └── js/            # JavaScript SDK (coming)
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
