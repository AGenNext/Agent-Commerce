"""
Shopify Adapter

Shopify: Catalog API, Checkout MCP, Storefront API.
Supports AI agents for commerce.

Docs: https://shopify.com/editions/winter2026
"""

from abc import ABC, abstractmethod
from typing import Any


class ShopifyAdapter(ABC):
    """
    Shopify Adapter.
    
    Supports:
    - Catalog API (products, search)
    - Checkout MCP
    - Storefront API
    - Agentic commerce
    
    Docs: https://shopify.com/editions/winter2026
    """
    
    def __init__(self, api_key: str | None = None, config: dict | None = None):
        self.api_key = api_key
        self.config = config or {}
        self.store_url = self.config.get("store_url", "https://store.myshopify.com")
    
    async def get_products(
        self,
        params: dict | None = None,
    ) -> dict:
        """Get products from catalog."""
        return {
            "products": [
                {
                    "id": 1,
                    "title": "Product",
                    "variants": [{"price": "29.99"}],
                }
            ]
        }
    
    async def search_products(
        self,
        query: str,
        limit: int = 10,
    ) -> dict:
        """Search products in catalog."""
        return {
            "products": [
                {"id": 1, "title": query, "price": "29.99"}
            ],
            "total": 1,
        }
    
    async def create_checkout(
        self,
        line_items: list[dict],
    ) -> dict:
        """Create Shopify checkout."""
        import uuid
        
        checkout_id = f"checkout_{uuid.uuid4().hex[:16]}"
        
        return {
            "id": checkout_id,
            "web_url": f"{self.store_url}/checkouts/{checkout_id}",
            "line_items": line_items,
        }
    
    async def get_checkout(
        self,
        checkout_id: str,
    ) -> dict:
        """Get checkout status."""
        return {
            "id": checkout_id,
            "ready": True,
            "completed": False,
        }
    
    async def add_to_cart(
        self,
        variant_id: str,
        quantity: int = 1,
    ) -> dict:
        """Add item to cart."""
        return {
            "variant_id": variant_id,
            "quantity": quantity,
            "status": "added",
        }
    
    # Base interface
    async def create_payment(
        self,
        amount: float,
        currency: str,
        **kwargs: Any
    ) -> dict:
        items = kwargs.get("line_items", [{"variant_id": 1, "quantity": 1}])
        return await self.create_checkout(items)
    
    async def verify_payment(
        self,
        payment_id: str
    ) -> dict:
        return await self.get_checkout(payment_id)
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: float | None = None
    ) -> dict:
        return {"id": payment_id, "status": "refunded"}