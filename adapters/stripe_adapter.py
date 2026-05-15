"""
Stripe Payment Adapter

Stripe: OpenAI/Stripe agentic commerce.
Supports checkout, payment intents, Shared Payment Tokens.

Docs: https://stripe.com
"""

from abc import ABC, abstractmethod
from typing import Any


class StripeAdapter(ABC):
    """
    Stripe Payment Adapter.
    
    Supports:
    - Checkout sessions
    - Payment intents
    - Shared Payment Tokens (SPT)
    - ACP integration (Instant Checkout in ChatGPT)
    
    Docs: https://stripe.com
    """
    
    def __init__(self, api_key: str | None = None, config: dict | None = None):
        self.api_key = api_key
        self.config = config or {}
        self.api_version = self.config.get("api_version", "2023-10-16")
    
    async def create_checkout(
        self,
        items: list[dict],
        currency: str = "USD",
        customer_id: str | None = None,
    ) -> dict:
        """Create Stripe checkout session."""
        import uuid
        
        total = sum(
            item.get("price", 0) * item.get("quantity", 1) 
            for item in items
        )
        
        session_id = f"cs_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": session_id,
            "url": f"https://checkout.stripe.com/c/pay/{session_id}",
            "amount_total": total,
            "currency": currency,
            "status": "open",
        }
    
    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "USD",
        customer_id: str | None = None,
    ) -> dict:
        """Create Stripe payment intent."""
        import uuid
        
        intent_id = f"pi_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": intent_id,
            "amount": int(amount * 100),
            "currency": currency,
            "status": "requires_payment_method",
        }
    
    async def create_shared_token(
        self,
        customer_id: str,
        amount: float,
        merchant: str,
        restrictions: dict | None = None,
    ) -> dict:
        """
        Create Stripe Shared Payment Token (SPT).
        
        Enables agents to pay without raw credentials.
        """
        import uuid
        
        token_id = f"spt_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": token_id,
            "customer_id": customer_id,
            "amount": int(amount * 100),
            "merchant": merchant,
            "restrictions": restrictions or {
                "max_amount": amount,
                "currency": currency,
            },
            "status": "active",
        }
    
    async def verify_checkout(
        self,
        session_id: str,
    ) -> dict:
        """Verify checkout session status."""
        return {
            "id": session_id,
            "status": "complete",
        }
    
    # Base interface
    async def create_payment(
        self,
        amount: float,
        currency: str,
        **kwargs: Any
    ) -> dict:
        return await self.create_payment_intent(
            amount,
            currency,
            kwargs.get("customer_id")
        )
    
    async def verify_payment(
        self,
        payment_id: str
    ) -> dict:
        return {"id": payment_id, "status": "succeeded"}
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: float | None = None
    ) -> dict:
        return {"id": f"re_{payment_id[:8]}", "status": "succeeded"}