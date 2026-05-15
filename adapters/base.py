"""
Base Payment Adapter Interface

Abstract base class for all payment adapters.
"""

from abc import ABC, abstractmethod
from typing import Any


class PaymentAdapter(ABC):
    """Base adapter interface for all payment providers."""
    
    @abstractmethod
    async def create_payment(
        self,
        amount: float,
        currency: str,
        **kwargs: Any
    ) -> dict:
        """Create a new payment."""
        pass
    
    @abstractmethod
    async def verify_payment(
        self,
        payment_id: str
    ) -> dict:
        """Verify payment status."""
        pass
    
    @abstractmethod
    async def refund_payment(
        self,
        payment_id: str,
        amount: float | None = None
    ) -> dict:
        """Refund a payment."""
        pass


# ============================================================
# ADAPTER FACTORY
# ============================================================

class PaymentAdapterFactory:
    """Factory for creating payment adapters."""
    
    @classmethod
    def create(
        cls,
        provider: str,
        api_key: str | None = None,
        config: dict | None = None,
    ) -> PaymentAdapter:
        """Create adapter by provider name."""
        
        adapters = {
            "ap2": "adapters.ap2_adapter:AP2Adapter",
            "x402": "adapters.x402_adapter:X402Adapter",
            "stripe": "adapters.stripe_adapter:StripeAdapter",
            "paypal": "adapters.paypal_adapter:PayPalAdapter",
            "mastercard": "adapters.mastercard_adapter:MastercardAdapter",
            "openbanking": "adapters.openbanking_adapter:OpenBankingAdapter",
            "mpp": "adapters.mpp_adapter:MPPAdapter",
            "shopify": "adapters.shopify_adapter:ShopifyAdapter",
        }
        
        if provider.lower() not in adapters:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Dynamic import
        import importlib
        module_path, class_name = adapters[provider.lower()].split(":")
        module = importlib.import_module(module_path)
        adapter_class = getattr(module, class_name)
        
        return adapter_class(api_key, config)
    
    @classmethod
    def list_providers(cls) -> list[str]:
        """List available providers."""
        return [
            "ap2", "x402", "stripe", "paypal", 
            "mastercard", "openbanking", "mpp", "shopify"
        ]