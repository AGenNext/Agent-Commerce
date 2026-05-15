"""
Payment Adapters Package

Modular adapters for agentic payments.

Sources:
- https://stripe.com/in/guides/agentic-commerce - Stripe agentic commerce
- https://developer.woocommerce.com/docs/apis/rest-api/v3/ - WooCommerce API

Adapters:
- ap2: Google/FIDO Agent Payments Protocol
- x402: Coinbase/Cloudflare stablecoin HTTP 402
- stripe: OpenAI/Stripe checkout
- paypal: PayPal agent payments
- mastercard: Mastercard Agent Pay
- openbanking: PSD2/SEPA
- mpp: Stripe/Tempo Machine Payments
- shopify: Shopify Catalog/Checkout

Usage:
    from adapters import PaymentAdapterFactory
    
    adapter = PaymentAdapterFactory.create("stripe", api_key="sk_xxx")
    payment = await adapter.create_payment(29.99, "USD")
"""

from adapters.base import PaymentAdapter, PaymentAdapterFactory
from adapters.ap2_adapter import AP2Adapter
from adapters.x402_adapter import X402Adapter
from adapters.stripe_adapter import StripeAdapter
from adapters.paypal_adapter import PayPalAdapter
from adapters.mastercard_adapter import MastercardAdapter
from adapters.openbanking_adapter import OpenBankingAdapter
from adapters.mpp_adapter import MPPAdapter
from adapters.shopify_adapter import ShopifyAdapter

__all__ = [
    "PaymentAdapter",
    "PaymentAdapterFactory",
    "AP2Adapter",
    "X402Adapter",
    "StripeAdapter",
    "PayPalAdapter",
    "MastercardAdapter",
    "OpenBankingAdapter",
    "MPPAdapter",
    "ShopifyAdapter",
]

__version__ = "1.0.0"