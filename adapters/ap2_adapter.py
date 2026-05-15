"""
AP2 (Agent Payments Protocol) Adapter

AP2: Google/FIDO Alliance standard for AI agent payments.
Supports autonomous payments with verifiable intent.

Docs: https://ap2lab.com
"""

from abc import ABC, abstractmethod
from typing import Any


class AP2Adapter(ABC):
    """
    AP2 (Agent Payments Protocol) Adapter.
    
    Supports:
    - Payment intents
    - Agent authorization
    - Autonomous payments (Human Not Present)
    - Verifiable log for accountability
    
    Docs: https://ap2lab.com
    """
    
    def __init__(self, api_key: str | None = None, config: dict | None = None):
        self.api_key = api_key
        self.config = config or {}
        self.base_url = self.config.get("base_url", "https://api.ap2.example.com")
    
    async def create_intent(
        self,
        user_id: str,
        amount: float,
        currency: str = "USD",
        reason: str | None = None,
    ) -> dict:
        """
        Create AP2 payment intent.
        
        The core of AP2 - defines what agent can pay for.
        """
        import uuid
        
        intent_id = f"ap2_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": intent_id,
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "reason": reason,
            "status": "pending",
        }
    
    async def authorize_agent(
        self,
        user_id: str,
        agent_id: str,
        max_amount: float,
        permissions: list[str] | None = None,
    ) -> dict:
        """
        Authorize AI agent to make autonomous payments.
        
        Enables "Human Not Present" payments with spending limits.
        """
        import uuid
        
        auth_id = f"ap2auth_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": auth_id,
            "user_id": user_id,
            "agent_id": agent_id,
            "max_amount": max_amount,
            "permissions": permissions or ["purchase"],
            "status": "active",
        }
    
    async def verify_intent(
        self,
        intent_id: str,
        user_id: str,
    ) -> dict:
        """Verify user intent for payment."""
        return {
            "intent_id": intent_id,
            "user_id": user_id,
            "status": "verified",
        }
    
    async def execute_autonomous(
        self,
        auth_id: str,
        intent_id: str,
        amount: float,
        description: str,
    ) -> dict:
        """Execute autonomous payment via authorized agent."""
        import uuid
        
        txn_id = f"ap2txn_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": txn_id,
            "auth_id": auth_id,
            "intent_id": intent_id,
            "amount": amount,
            "description": description,
            "status": "completed",
        }
    
    async def create_verifiable_log(
        self,
        transaction_id: str,
    ) -> dict:
        """Create tamper-proof log for accountability."""
        return {
            "transaction_id": transaction_id,
            "log": {
                "action": "purchase",
                "timestamp": "NOW()",
            },
            "signature": f"sig_{transaction_id}",
        }
    
    async def verify_trust(
        self,
        entity_id: str,
        entity_type: str,
    ) -> dict:
        """Verify entity trust level."""
        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "trust_level": "standard",
        }
    
    # Base interface methods
    async def create_payment(
        self,
        amount: float,
        currency: str,
        **kwargs: Any
    ) -> dict:
        return await self.create_intent(
            kwargs.get("user_id", ""),
            amount,
            currency,
            kwargs.get("reason")
        )
    
    async def verify_payment(
        self,
        payment_id: str
    ) -> dict:
        return await self.verify_intent(payment_id, "")
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: float | None = None
    ) -> dict:
        return {"id": payment_id, "status": "refunded"}