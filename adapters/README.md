# Payment Adapters

Modular payment provider adapters for agentic commerce.

## Installation

```bash
pip install -e .
```

## Usage

```python
import asyncio
from adapters import PaymentAdapterFactory

async def main():
    # Create adapter
    stripe = PaymentAdapterFactory.create("stripe", api_key="sk_xxx")
    
    # Create payment
    payment = await stripe.create_payment(29.99, "USD")
    print(f"Payment: {payment}")
    
    # List providers
    print(f"Providers: {PaymentAdapterFactory.list_providers()}")

asyncio.run(main())
```

## Adapters

| Adapter | Provider | Protocol |
|---------|----------|----------|
| `AP2Adapter` | Google/FIDO | AP2 |
| `X402Adapter` | Coinbase | x402 |
| `StripeAdapter` | Stripe | Stripe |
| `PayPalAdapter` | PayPal | PayPal |
| `MastercardAdapter` | Mastercard | Mastercard |
| `OpenBankingAdapter` | Open Banking | PSD2 |
| `MPPAdapter` | Stripe/Tempo | MPP |
| `ShopifyAdapter` | Shopify | Shopify |

## Each Adapter

```python
from adapters import StripeAdapter

adapter = StripeAdapter("sk_xxx")

# Create checkout
checkout = await adapter.create_checkout([
    {"name": "Product", "price": 2999, "quantity": 1}
])

# Create payment intent
intent = await adapter.create_payment_intent(29.99, "USD")

# Shared Payment Token
spt = await adapter.create_shared_token("cust_xxx", 100, "merchant")
```

## Base Interface

All adapters implement:

```python
await adapter.create_payment(amount, currency, **kwargs)
await adapter.verify_payment(payment_id)
await adapter.refund_payment(payment_id, amount)
```

## License

MIT