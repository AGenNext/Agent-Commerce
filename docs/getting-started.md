# Getting Started

## Installation

```bash
# Clone repository
git clone https://github.com/AGenNext/Agent-Commerce.git
cd Agent-Commerce

# Install dependencies
pip install -r requirements.txt
```

## Local Development

```bash
# Run tests
python test_e2e.py

# Start API server
python server.py
```

## Docker

```bash
# Build container
docker build -t agent-commerce .

# Run container
docker run -p 8000:8000 agent-commerce
```

## First Product

```python
from store_manager import StoreManager

store = StoreManager(config={})

# Create product
product = await store.create_product({
    "title": "My First Product",
    "price": 29.99,
    "description": "A great product"
})

print(f"Created: {product['id']}")
```

## First Payment

```python
from adapters import PaymentAdapterFactory

# Choose provider
adapter = PaymentAdapterFactory.create("stripe")

# Create payment
payment = await adapter.create_payment(
    amount=29.99,
    currency="USD",
    user_id="user_123"
)

print(f"Payment ID: {payment['id']}")
```

## Next Steps

- [API Reference](api-reference.md)
- [SDK Guide](sdk-guide.md)
- [Payment Providers](providers.md)