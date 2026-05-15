#!/usr/bin/env python3
"""
End-to-End Test Suite

Tests all agents and integrations together.
"""

import asyncio
import sys
from datetime import datetime

# Import all modules
from surrealdb_layer import SurrealDBLayer
from store_manager import StoreManager, PlatformFactory
from site_admin import SiteAdmin
from vendor_agent import VendorAgent, VendorPanel
from marketplace_manager import MarketplaceManager
from adapters import PaymentAdapterFactory


# Shared DB instance
DB: SurrealDBLayer | None = None


async def get_db() -> SurrealDBLayer:
    """Get or create shared DB instance."""
    global DB
    if DB is None:
        DB = SurrealDBLayer()
        await DB.connect()
        
        # Initialize tables
        await DB.create_table("products")
        await DB.create_table("orders")
        await DB.create_table("customers")
        await DB.create_table("agents")
        await DB.create_table("vendors")
        await DB.create_table("discounts")
        
        # Register all agents
        await DB.register_agent({"id": "agent_commerce", "name": "Commerce Agent", "type": "commerce"})
        await DB.register_agent({"id": "agent_store", "name": "Store Manager", "type": "store"})
        await DB.register_agent({"id": "agent_admin", "name": "Site Admin", "type": "admin"})
        await DB.register_agent({"id": "agent_vendor", "name": "Vendor Agent", "type": "vendor"})
        await DB.register_agent({"id": "agent_marketplace", "name": "Marketplace Manager", "type": "marketplace"})
    
    return DB


async def test_centralized_db():
    """Test centralized DB."""
    print("\n" + "="*50)
    print("TESTING: Centralized SurrealDB Layer")
    print("="*50)
    
    db = await get_db()
    
    # Health check
    health = await db.health()
    print(f"✓ DB Status: {health['status']}")
    print(f"✓ Tables: {health['tables']}")
    print(f"✓ Records: {health['records']}")
    
    # List agents
    agents = await db.list_agents()
    print(f"✓ Registered Agents: {len(agents)}")
    for agent in agents:
        print(f"  - {agent['name']}: {agent['type']}")
    
    # Create sample data
    product = await db.create("products", {
        "title": "Test Product",
        "price": 29.99,
        "inventory": 100
    })
    print(f"✓ Product: {product['id']}")
    
    order = await db.create("orders", {
        "product_id": product["id"],
        "total": 29.99,
        "status": "pending"
    })
    print(f"✓ Order: {order['id']}")
    
    # Create relation
    rel = await db.relate(order["id"], product["id"], "includes")
    print(f"✓ Relation: {rel['id']}")
    
    # Search
    results = await db.search("products", "test")
    print(f"✓ Search: {len(results)} results")
    
    return True


async def test_store_manager():
    """Test Store Manager."""
    print("\n" + "="*50)
    print("TESTING: Store Manager")
    print("="*50)
    
    store = StoreManager(config={"store_name": "Test Store"})
    
    card = store.get_agent_card()
    print(f"✓ Agent: {card['name']}")
    print(f"✓ Skills: {len(card['skills'])}")
    
    # Products
    product = await store.create_product({
        "title": "Test Product",
        "price": 29.99,
        "inventory": 100,
    })
    print(f"✓ Create product: {product['id']}")
    
    # Orders
    order = await store.create_order({
        "customer_id": "cust_001",
        "email": "test@example.com",
        "line_items": [
            {"product_id": product["id"], "price": 29.99, "quantity": 1}
        ],
    })
    print(f"✓ Create order: {order['id']} - ${order['total']}")
    
    # Dashboard
    dashboard = await store.get_dashboard()
    print(f"✓ Dashboard: {dashboard}")
    
    # Discounts
    discount = await store.create_discount({
        "code": "TEST20",
        "type": "percentage",
        "value": 20,
    })
    print(f"✓ Discount: {discount['code']}")
    
    return True


async def test_platform_integrations():
    """Test platform integrations."""
    print("\n" + "="*50)
    print("TESTING: Platform Integrations")
    print("="*50)
    
    store = StoreManager(config={"store_name": "Test"})
    
    for platform in ["woocommerce", "shopify", "mercur"]:
        integration = PlatformFactory.create_platform(platform, {"api_key": "test"})
        result = await integration.sync_products(store)
        print(f"✓ {platform}: {result['message']}")
    
    return True


async def test_payment_adapters():
    """Test all payment adapters."""
    print("\n" + "="*50)
    print("TESTING: Payment Adapters")
    print("="*50)
    
    providers = PaymentAdapterFactory.list_providers()
    print(f"✓ Providers: {providers}")
    
    results = {}
    for provider in providers:
        adapter = PaymentAdapterFactory.create(provider)
        result = await adapter.create_payment(29.99, "USD", user_id="test")
        results[provider] = result["id"]
        print(f"✓ {provider}: {result['id'][:20]}...")
    
    return True


async def test_site_admin():
    """Test Site Admin."""
    print("\n" + "="*50)
    print("TESTING: Site Admin")
    print("="*50)
    
    admin = SiteAdmin()
    
    card = admin.get_agent_card()
    print(f"✓ Agent: {card['name']}")
    print(f"✓ Skills: {len(card['skills'])}")
    
    # Settings
    site = await admin.get_site_info()
    print(f"✓ Site: {site.get('name')}")
    
    # Users
    users = await admin.get_users()
    print(f"✓ Users: {len(users.get('users', []))}")
    
    # Roles
    roles = await admin.get_roles()
    print(f"✓ Roles: {len(roles.get('roles', []))}")
    
    # API keys
    api_key = await admin.create_api_key("Test Key", ["read"])
    print(f"✓ API Key: {api_key['api_key'][:20]}...")
    
    return True


async def test_vendor_agent():
    """Test Vendor Agent."""
    print("\n" + "="*50)
    print("TESTING: Vendor Agent")
    print("="*50)
    
    vendor = VendorAgent()
    
    card = vendor.get_agent_card()
    print(f"✓ Agent: {card['name']}")
    print(f"✓ Skills: {len(card['skills'])}")
    
    # Products
    product = await vendor.create_product("vendor_001", {
        "title": "Vendor Product",
        "price": 49.99,
        "inventory": 50,
    })
    print(f"✓ Product: {product['id']}")
    
    # Dashboard
    dashboard = await vendor.get_dashboard("vendor_001")
    print(f"✓ Dashboard: {dashboard}")
    
    return True


async def test_marketplace_manager():
    """Test Marketplace Manager."""
    print("\n" + "="*50)
    print("TESTING: Marketplace Manager")
    print("="*50)
    
    mgr = MarketplaceManager()
    
    card = mgr.get_agent_card()
    print(f"✓ Agent: {card['name']}")
    print(f"✓ Skills: {len(card['skills'])}")
    
    # Settings
    settings = await mgr.get_settings()
    print(f"✓ Settings: {settings.get('name')}")
    
    # Vendors
    vendors = await mgr.list_vendors()
    print(f"✓ Vendors: {len(vendors.get('vendors', []))}")
    
    # Dashboard
    dashboard = await mgr.get_dashboard()
    print(f"✓ Dashboard: {dashboard}")
    
    # Tax codes
    taxes = await mgr.get_tax_codes()
    print(f"✓ Tax codes: {len(taxes.get('codes', []))}")
    
    # Messaging
    conv = await mgr.create_conversation(["buyer_001", "vendor_001"])
    print(f"✓ Conversation: {conv['id']}")
    
    # Headless API
    client = await mgr.create_api_client("Test App", ["read"])
    print(f"✓ API Client: {client['client_id'][:20]}...")
    
    # Mercur Connect
    sync = await mgr.mercur_connect_sync_products("vendor_001", "shopify")
    print(f"✓ Mercur Connect: {sync['platform']}")
    
    return True


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("END-TO-END TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    
    tests = [
        ("UCP Agent", test_ucp_agent),
        ("Store Manager", test_store_manager),
        ("Platform Integrations", test_platform_integrations),
        ("Payment Adapters", test_payment_adapters),
        ("Site Admin", test_site_admin),
        ("Vendor Agent", test_vendor_agent),
        ("Marketplace Manager", test_marketplace_manager),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            result = await test_fn()
            if result:
                passed += 1
                print(f"\n✓ {name}: PASSED")
        except Exception as e:
            failed += 1
            print(f"\n✗ {name}: FAILED - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed > 0:
        sys.exit(1)
    
    print("\n✓ ALL TESTS PASSED!")
    return True


if __name__ == "__main__":
    asyncio.run(main())