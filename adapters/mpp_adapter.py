"""
MPP (Machine Payments Protocol) Adapter

MPP: Stripe/Tempo machine-to-machine payments.

Docs: https://stripe.com/blog/machine-payments-protocol
"""

from abc import ABC, abstractmethod
from typing import Any


class MPPAdapter(ABC):
    """
    Machine Payments Protocol (MPP) Adapter.
    
    Co-authored by Stripe and Tempo.
    Enables agents to pay for API calls, microtransactions, resources.
    
    Docs: https://stripe.com/blog/machine-payments-protocol
    """
    
    def __init__(self, api_key: str | None = None, config: dict | None = None):
        self.api_key = api_key
        self.config = config or {}
    
    async def create_payment_request(
        self,
        resource: str,
        amount: float,
        currency: str = "USD",
        metadata: dict | None = None,
    ) -> dict:
        """Create MPP payment request for resource."""
        import uuid
        
        request_id = f"mppreq_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": request_id,
            "resource": resource,
            "amount": amount,
            "currency": currency,
            "status": "pending",
            "metadata": metadata or {},
        }
    
    async def authorize_payment(
        self,
        request_id: str,
        payment_method_id: str,
    ) -> dict:
        """Authorize payment for resource."""
        import uuid
        
        auth_id = f"mppauth_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": auth_id,
            "request_id": request_id,
            "payment_method_id": payment_method_id,
            "status": "authorized",
        }
    
    async def deliver_resource(
        self,
        authorization_id: str,
    ) -> dict:
        """Deliver resource after payment."""
        return {
            "resource_id": authorization_id,
            "status": "delivered",
        }
    
    async def get_usage(
        self,
        resource_id: str,
    ) -> dict:
        """Get resource usage metrics."""
        return {
            "resource_id": resource_id,
            "calls": 0,
            "total_spent": 0,
        }
    
    # Base interface
    async def create_payment(
        self,
        amount: float,
        currency: str,
        **kwargs: Any
    ) -> dict:
        return await self.create_payment_request(
            kwargs.get("resource", "default"),
            amount,
            currency
        )
    
    async def verify_payment(
        self,
        payment_id: str
    ) -> dict:
        return {"id": payment_id, "status": "completed"}
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: float | None = None
    ) -> dict:
        return {"id": f"mppref_{payment_id[:8]}", "status": "completed"}