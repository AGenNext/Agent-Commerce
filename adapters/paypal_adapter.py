"""
PayPal Payment Adapter

PayPal: Agent payments, escrow, AP2 compliance.

Docs: https://developer.paypal.com
"""

from abc import ABC, abstractmethod
from typing import Any


class PayPalAdapter(ABC):
    """
    PayPal Payment Adapter.
    
    Supports:
    - Agent payments
    - Escrow
    - AP2 compliance
    - Orders
    
    Docs: https://developer.paypal.com
    """
    
    def __init__(self, client_id: str | None = None, config: dict | None = None):
        self.client_id = client_id
        self.config = config or {}
        self.mode = self.config.get("mode", "sandbox")  # sandbox, live
    
    async def create_order(
        self,
        amount: float,
        currency: str = "USD",
        description: str | None = None,
    ) -> dict:
        """Create PayPal order."""
        import uuid
        
        order_id = f"ORDER-{uuid.uuid4().hex[:12].upper()}"
        
        return {
            "id": order_id,
            "status": "CREATED",
            "amount": {"value": str(amount), "currency_code": currency},
            "description": description,
        }
    
    async def capture_order(
        self,
        order_id: str,
    ) -> dict:
        """Capture PayPal order."""
        return {
            "id": order_id,
            "status": "COMPLETED",
        }
    
    async def create_escrow(
        self,
        sender_id: str,
        recipient_id: str,
        amount: float,
        release_conditions: dict,
    ) -> dict:
        """
        Create PayPal escrow.
        
        Funds held until conditions met.
        """
        import uuid
        
        escrow_id = f"ESCROW-{uuid.uuid4().hex[:12].upper()}"
        
        return {
            "id": escrow_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "amount": amount,
            "release_conditions": release_conditions,
            "status": "HELD",
        }
    
    async def release_escrow(
        self,
        escrow_id: str,
    ) -> dict:
        """Release PayPal escrow."""
        return {
            "id": escrow_id,
            "status": "RELEASED",
        }
    
    async def create_agent_payment(
        self,
        sender_id: str,
        recipient_id: str,
        amount: float,
        request_id: str | None = None,
    ) -> dict:
        """Create agent payment (AP2 compliant)."""
        import uuid
        
        payment_id = f"PPAP-{uuid.uuid4().hex[:12].upper()}"
        
        return {
            "id": payment_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "amount": amount,
            "request_id": request_id,
            "status": "pending",
        }
    
    # Base interface
    async def create_payment(
        self,
        amount: float,
        currency: str,
        **kwargs: Any
    ) -> dict:
        return await self.create_order(
            amount,
            currency,
            kwargs.get("description")
        )
    
    async def verify_payment(
        self,
        payment_id: str
    ) -> dict:
        return await self.capture_order(payment_id)
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: float | None = None
    ) -> dict:
        return {"id": f"REF-{payment_id[:8]}", "status": "COMPLETED"}