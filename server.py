# Agent-Commerce FastAPI Server
# Run: python3 server.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import asyncio

# Import all agents
from store_manager import StoreManager
from site_admin import SiteAdmin
from vendor_agent import VendorAgent
from marketplace_manager import MarketplaceManager
from surrealdb_layer import SurrealDBLayer

# Create FastAPI app
app = FastAPI(
    title="Agent-Commerce API",
    description="UCP Commerce Agents with SurrealDB",
    version="1.0.0"
)

# Initialize DB
db = None
stores = {}
vendors = {}

@app.on_event("startup")
async def startup():
    global db
    db = SurrealDBLayer()
    await db.connect()
    await db.create_table("products")
    await db.create_table("orders")
    await db.create_table("agents")
    print("✅ SurrealDB connected")

@app.get("/")
async def root():
    return {"name": "Agent-Commerce", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "db": "connected" if db else "disconnected"}

# Store Manager endpoints
@app.post("/api/store/products")
async def create_product(data: dict):
    store_key = data.get("store_id", "default")
    if store_key not in stores:
        stores[store_key] = StoreManager(config={})
    return await stores[store_key].create_product(data)

@app.get("/api/store/products")
async def list_products():
    store = stores.get("default", StoreManager(config={}))
    return await store.list_products()

@app.post("/api/store/orders")
async def create_order(data: dict):
    store = stores.get("default", StoreManager(config={}))
    return await store.create_order(data)

@app.get("/api/store/dashboard")
async def dashboard():
    store = stores.get("default", StoreManager(config={}))
    return await store.get_dashboard()

# Site Admin endpoints
@app.get("/api/admin/info")
async def site_info():
    admin = SiteAdmin()
    return await admin.get_site_info()

@app.get("/api/admin/users")
async def users():
    admin = SiteAdmin()
    return await admin.get_users()

@app.get("/api/admin/roles")
async def roles():
    admin = SiteAdmin()
    return await admin.get_roles()

# Vendor endpoints
@app.post("/api/vendor/products")
async def vendor_product(data: dict):
    vendor_id = data.get("vendor_id")
    if vendor_id not in vendors:
        vendors[vendor_id] = VendorAgent()
    return await vendors[vendor_id].create_product(vendor_id, data)

@app.get("/api/vendor/{vendor_id}/dashboard")
async def vendor_dashboard(vendor_id: str):
    if vendor_id not in vendors:
        vendors[vendor_id] = VendorAgent()
    return await vendors[vendor_id].get_dashboard(vendor_id)

# Marketplace endpoints
@app.get("/api/marketplace/settings")
async def mp_settings():
    mgr = MarketplaceManager()
    return await mgr.get_settings()

@app.get("/api/marketplace/dashboard")
async def mp_dashboard():
    mgr = MarketplaceManager()
    return await mgr.get_dashboard()

@app.post("/api/marketplace/conversations")
async def create_conversation(participants: list):
    mgr = MarketplaceManager()
    return await mgr.create_conversation(participants)

# Payment endpoints
@app.post("/api/payments/{provider}")
async def create_payment(provider: str, data: dict):
    from adapters import PaymentAdapterFactory
    adapter = PaymentAdapterFactory.create(provider)
    return await adapter.create_payment(
        data.get("amount", 29.99),
        data.get("currency", "USD"),
        user_id=data.get("user_id", "test")
    )

@app.get("/api/providers")
async def providers():
    from adapters import PaymentAdapterFactory
    return {"providers": PaymentAdapterFactory.list_providers()}

# Database operations
@app.get("/api/db/health")
async def db_health():
    if db:
        return await db.health()
    return {"status": "not_initialized"}

# Main entry
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)