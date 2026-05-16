# Agent-Commerce SDK Documentation

## Installation

```bash
pip install agent-commerce
```

## Quick Start

```python
from agent_commerce import Client
import asyncio

async def main():
    # Initialize client
    client = Client(api_key="sk_your_api_key")
    
    # Create a product
    product = await client.products.create({
        "title": "AI Widget",
        "price": 29.99,
        "description": "An awesome AI-powered product"
    })
    
    print(f"Created product: {product['id']}")

asyncio.run(main())
```

## Configuration

```python
# With custom base URL
client = Client(
    api_key="sk_...",
    base_url="https://api.example.com"  # default: http://localhost:8000
)

# With timeout
client = Client(
    api_key="sk_...",
    timeout=60  # default: 30 seconds
)
```

## Products API

### Create Product

```python
product = await client.products.create({
    "title": "Product Name",
    "price": 29.99,
    "description": "Product description",
    "sku": "SKU123",
    "inventory": 100,
    "category": "electronics"
})
```

### List Products

```python
# All products
products = await client.products.list()

# With limit
products = await client.products.list(limit=50)

# Search
products = await client.products.search("widget")
```

### Get Product

```python
product = await client.products.get("prod_abc123")
```

### Update Product

```python
product = await client.products.update("prod_abc123", {
    "price": 39.99,
    "inventory": 50
})
```

### Delete Product

```python
result = await client.products.delete("prod_abc123")
```

## Orders API

### Create Order

```python
order = await client.orders.create({
    "customer_id": "cust_123",
    "email": "customer@example.com",
    "line_items": [
        {"product_id": "prod_abc", "quantity": 2}
    ],
    "shipping_address": {
        "line1": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "postal": "94102",
        "country": "US"
    }
})
```

### List Orders

```python
# All orders
orders = await client.orders.list()

# By status
orders = await client.orders.list(status="pending")
```

### Update Order

```python
order = await client.orders.update("order_xyz", {
    "status": "processing"
})
```

### Cancel Order

```python
order = await client.orders.cancel("order_xyz", "Customer request")
```

### Fulfill Order

```python
order = await client.orders.fulfill("order_xyz")
```

## Payments API

### Create Payment

```python
# Stripe
payment = await client.payments.create(
    "stripe",
    29.99,
    "USD",
    user_id="user_123"
)

# PayPal
payment = await client.payments.create(
    "paypal",
    29.99,
    "USD",
    user_id="user_123"
)
```

### Verify Payment

```python
result = await client.payments.verify("stripe", "pi_abc123")
```

### Refund Payment

```python
# Full refund
refund = await client.payments.refund("stripe", "pi_abc123")

# Partial refund
refund = await client.payments.refund("stripe", "pi_abc123", 10.00)
```

### List Providers

```python
providers = await client.payments.list_providers()
# {"providers": ["ap2", "x402", "stripe", "paypal", "mastercard", "openbanking", "mpp", "shopify"]}
```

## Webhooks

```python
# Webhook payload example
{
    "event": "order.created",
    "data": {
        "id": "order_xyz",
        "customer_id": "cust_123",
        "total": 29.99
    },
    "timestamp": "2026-05-15T12:00:00Z"
}
```

Supported events:
- `product.created`
- `product.updated`
- `product.deleted`
- `order.created`
- `order.updated`
- `order.fulfilled`
- `order.cancelled`
- `payment.created`
- `payment.succeeded`
- `payment.failed`

## Error Handling

```python
from agent_commerce import (
    Client, 
    AgentCommerceError, 
    AuthenticationError, 
    NotFoundError
)

try:
    product = await client.products.get("prod_invalid")
except NotFoundError:
    print("Product not found")
except AuthenticationError:
    print("Invalid API key")
except AgentCommerceError as e:
    print(f"Error: {e}")
```

## Sync Client

For blocking (synchronous) usage:

```python
from agent_commerce import SyncClient

with SyncClient(api_key="sk_...") as client:
    product = client.products.create({"title": "Widget"})
    print(product['id'])
```

## Environment Variables

```bash
export AGENT_COMMERCE_API_KEY="sk_..."
export AGENT_COMMERCE_BASE_URL="https://api.example.com"
```