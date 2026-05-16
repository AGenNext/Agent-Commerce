"""
AE Commerce - Autonomous E-Commerce Platform
========================================

A complete e-commerce platform with:
- AI Commerce Agents
- Multi-vendor Marketplace  
- 8 Payment Protocols
- SurrealDB Backend

Usage:
    python ae_commerce.py
"""

import asyncio
import json
from datetime import datetime

# Core modules
from store_manager import StoreManager
from marketplace_manager import MarketplaceManager
from site_admin import SiteAdmin
from vendor_agent import VendorAgent
from surrealdb_layer import SurrealDBLayer

# Payment adapters
from adapters import PaymentAdapterFactory


class AECommerce:
    """
    Main AE Commerce Platform
    
    Usage:
        platform = AECommerce()
        await platform.initialize()
        
        # Create vendor store
        vendor = await platform.create_vendor("Acme Corp")
        
        # Add products
        product = await platform.add_product(vendor["id"], {
            "title": "AI Widget",
            "price": 29.99
        })
        
        # Process payment
        payment = await platform.process_payment(
            product["price"],
            "stripe"
        )
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.db = None
        self.stores = {}
        self.admins = {}
        self.vendors = {}
    
    async def initialize(self):
        """Initialize the platform."""
        # Connect to SurrealDB
        self.db = SurrealDBLayer()
        
        # Use in-memory for demo
        await self.db.connect()
        
        # Create tables
        await self.db.create_table("vendors")
        await self.db.create_table("products")
        await self.db.create_table("orders")
        await self.db.create_table("customers")
        await self.db.create_table("payments")
        
        print("✅ AE Commerce initialized")
        
        return self
    
    async def create_vendor(self, name: str, data: dict = None) -> dict:
        """Create a new vendor store."""
        vendor_data = {
            "name": name,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        if data:
            vendor_data.update(data)
        
        # Store in DB
        result = await self.db.create("vendors", vendor_data)
        
        # Initialize store manager
        store = StoreManager(config={"vendor_id": result["id"]})
        self.stores[result["id"]] = store
        
        # Initialize vendor agent
        vendor = VendorAgent()
        self.vendors[result["id"]] = vendor
        
        print(f"✅ Vendor created: {name}")
        
        return result
    
    async def add_product(self, vendor_id: str, product_data: dict) -> dict:
        """Add a product to a vendor store."""
        # Add vendor_id to product
        product_data["vendor_id"] = vendor_id
        
        # Store directly in DB
        product = await self.db.create("products", product_data)
        
        print(f"✅ Product added: {product_data.get('title')}")
        
        return product
    
    async def list_products(self, vendor_id: str = None) -> list:
        """List all products."""
        products = await self.db.select("products")
        
        if vendor_id:
            products = [p for p in products if p.get("vendor_id") == vendor_id]
        
        return products
    
    async def create_order(self, vendor_id: str, order_data: dict) -> dict:
        """Create an order."""
        store = self.stores.get(vendor_id)
        
        if not store:
            store = StoreManager(config={"vendor_id": vendor_id})
            self.stores[vendor_id] = store
        
        order = await store.create_order(order_data)
        
        print(f"✅ Order created: {order.get('id')}")
        
        return order
    
    async def process_payment(
        self,
        amount: float,
        provider: str = "stripe",
        currency: str = "USD",
        user_id: str = None
    ) -> dict:
        """Process a payment."""
        adapter = PaymentAdapterFactory.create(provider)
        
        payment = await adapter.create_payment(
            amount=amount,
            currency=currency,
            user_id=user_id or "anonymous"
        )
        
        print(f"✅ Payment processed: {provider} - {amount} {currency}")
        
        return payment
    
    async def verify_payment(self, provider: str, payment_id: str) -> dict:
        """Verify a payment."""
        adapter = PaymentAdapterFactory.create(provider)
        
        return await adapter.verify_payment(payment_id)
    
    async def refund_payment(
        self,
        provider: str,
        payment_id: str,
        amount: float = None
    ) -> dict:
        """Refund a payment."""
        adapter = PaymentAdapterFactory.create(provider)
        
        return await adapter.refund_payment(payment_id, amount)
    
    async def get_dashboard(self, vendor_id: str = None) -> dict:
        """Get dashboard metrics."""
        if vendor_id:
            store = self.stores.get(vendor_id)
            if store:
                return await store.get_dashboard()
        
        # Platform dashboard
        return {
            "vendors": len(self.stores),
            "products": len(await self.db.select("products")),
            "orders": len(await self.db.select("orders")),
            "providers": PaymentAdapterFactory.list_providers()
        }
    
    async def get_marketplace_settings(self) -> dict:
        """Get marketplace settings."""
        mgr = MarketplaceManager()
        return await mgr.get_settings()
    
    async def get_admin_info(self) -> dict:
        """Get admin info."""
        admin = SiteAdmin()
        return await admin.get_site_info()
    
    async def close(self):
        """Close connections."""
        print("👋 AE Commerce closed")


# Demo function
async def demo():
    """Run a demo of AE Commerce."""
    print("=" * 50)
    print("AE COMMERCE DEMO")
    print("=" * 50)
    
    # Initialize
    platform = AECommerce()
    await platform.initialize()
    
    # Create vendor
    vendor = await platform.create_vendor("Acme AI", {
        "email": "contact@acme.ai"
    })
    
    # Add products
    products = [
        {"title": "AI Widget Pro", "price": 49.99, "category": "AI Tools"},
        {"title": "GPT-5 Access", "price": 99.99, "category": "AI Access"},
        {"title": "AI Analytics", "price": 29.99, "category": "Analytics"}
    ]
    
    for product_data in products:
        await platform.add_product(vendor["id"], product_data)
    
    # List products
    print("\n📦 Products:")
    all_products = await platform.list_products(vendor["id"])
    for p in all_products:
        print(f"  - {p.get('title')}: ${p.get('price')}")
    
    # Create order
    order = await platform.create_order(vendor["id"], {
        "customer_id": "cust_123",
        "items": [
            {"product_id": all_products[0]["id"], "quantity": 1}
        ]
    })
    
    # Process payment
    payment = await platform.process_payment(49.99, "stripe", "USD", "user_123")
    
    # Get dashboard
    print("\n📊 Dashboard:")
    dashboard = await platform.get_dashboard(vendor["id"])
    print(f"  Vendors: {dashboard.get('vendors', 0)}")
    print(f"  Products: {dashboard.get('products', 0)}")
    
    # Payment providers
    print("\n💳 Payment Providers:")
    providers = PaymentAdapterFactory.list_providers()
    for p in providers:
        print(f"  - {p}")
    
    # Close
    await platform.close()
    
    print("\n" + "=" * 50)
    print("✅ DEMO COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(demo())