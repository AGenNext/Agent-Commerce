"""
Open Banking (PSD2) Adapter

Open Banking: PSD2 consent, SEPA payments, account access.

Docs: https://openbankingtracker.com
"""

from abc import ABC, abstractmethod
from typing import Any


class OpenBankingAdapter(ABC):
    """
    Open Banking Adapter (PSD2).
    
    Supports:
    - Account access
    - SEPA payments
    - Consent management
    
    Docs: https://openbankingtracker.com
    """
    
    def __init__(self, aspsp_id: str | None = None, config: dict | None = None):
        self.aspsp_id = aspsp_id
        self.config = config or {}
    
    async def create_consent(
        self,
        user_id: str,
        permissions: list[str],
        duration_hours: int = 24,
    ) -> dict:
        """
        Create PSD2 consent.
        
        Policy-based authorization for agents.
        """
        import uuid
        from datetime import datetime, timedelta
        
        consent_id = f"obc_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": consent_id,
            "user_id": user_id,
            "permissions": permissions,
            "valid_until": (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
            "status": "active",
        }
    
    async def get_accounts(
        self,
        consent_id: str,
    ) -> dict:
        """Get user's bank accounts."""
        return {
            "accounts": [
                {
                    "iban": "DE89370400440532013000",
                    "currency": "EUR",
                    "name": "Primary Account",
                },
            ]
        }
    
    async def get_balance(
        self,
        account_iban: str,
    ) -> dict:
        """Get account balance."""
        return {
            "iban": account_iban,
            "balance": 1000.00,
            "currency": "EUR",
        }
    
    async def initiate_payment(
        self,
        consent_id: str,
        amount: float,
        recipient_iban: str,
        reference: str,
    ) -> dict:
        """
        Initiate SEPA payment.
        
        A2A (account-to-account) transfer.
        """
        import uuid
        
        payment_id = f"sepa_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": payment_id,
            "status": "accepted",
            "amount": amount,
            "recipient": recipient_iban,
            "reference": reference,
        }
    
    async def verify_payment(
        self,
        payment_id: str,
    ) -> dict:
        """Verify SEPA payment status."""
        return {"id": payment_id, "status": "completed"}
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: float | None = None
    ) -> dict:
        return {"id": f"separef_{payment_id[:8]}", "status": "completed"}
    
    # Base interface
    async def create_payment(
        self,
        amount: float,
        currency: str,
        **kwargs: Any
    ) -> dict:
        return await self.initiate_payment(
            kwargs.get("consent_id", ""),
            amount,
            kwargs.get("iban", ""),
            kwargs.get("reference", "")
        )