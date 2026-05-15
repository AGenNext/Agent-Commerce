"""
x402 Payment Adapter

x402: Coinbase/Cloudflare HTTP 402 payment protocol.
Uses stablecoin payments over HTTP for AI agents.

Docs: https://developers.cloudflare.com/agents/agentic-payments/
"""

from abc import ABC, abstractmethod
from typing import Any


class X402Adapter(ABC):
    """
    x402 Payment Adapter.
    
    HTTP 402 Payment Required for AI agents.
    Uses stablecoin payments (USDC on Base, Ethereum, Solana).
    
    Docs: https://developers.cloudflare.com/agents/agentic-payments/
    """
    
    def __init__(self, api_key: str | None = None, config: dict | None = None):
        self.api_key = api_key
        self.config = config or {}
        self.network = self.config.get("network", "base")  # base, eth, sol
    
    async def create_challenge(
        self,
        resource: str,
        amount: int,  # In smallest units (cents for USD)
        currency: str = "USDC",
    ) -> dict:
        """
        Create x402 payment challenge.
        
        Returns challenge that client must satisfy with payment.
        Uses HTTP 402 status code.
        """
        import uuid
        
        challenge_id = f"x402_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": challenge_id,
            "resource": resource,
            "amount": amount,
            "currency": currency,
            "status": "pending",
            "headers": {
                "PAYMENT-REQUIRED": f"amount={amount},currency={currency}",
            },
        }
    
    async def verify_proof(
        self,
        challenge_id: str,
        payment_proof: dict,
    ) -> dict:
        """
        Verify payment proof.
        
        In production: verify on-chain transaction.
        """
        return {
            "challenge_id": challenge_id,
            "status": "authorized",
            "verified": True,
        }
    
    async def generate_receipt(
        self,
        challenge_id: str,
        transaction_id: str,
    ) -> dict:
        """Generate payment receipt."""
        return {
            "receipt_id": f"receipt_{transaction_id}",
            "challenge_id": challenge_id,
            "status": "paid",
            "PAYMENT-RESPONSE": {
                "transaction_id": transaction_id,
            },
        }
    
    async def get_payment_url(
        self,
        challenge_id: str,
    ) -> dict:
        """Get payment URL for user."""
        return {
            "url": f"https://pay.example.com/{challenge_id}",
            "networks": ["base", "ethereum", "solana"],
        }
    
    # Base interface
    async def create_payment(
        self,
        amount: float,
        currency: str,
        **kwargs: Any
    ) -> dict:
        resource = kwargs.get("resource", "default")
        cents = int(amount * 100)
        return await self.create_challenge(resource, cents, currency)
    
    async def verify_payment(
        self,
        payment_id: str
    ) -> dict:
        return await self.verify_proof(payment_id, {})
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: float | None = None
    ) -> dict:
        return {"id": payment_id, "status": "refunded"}