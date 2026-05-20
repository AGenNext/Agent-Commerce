# Agent-Commerce FastAPI Server
# Run: python3 server.py

import logging
import os
import secrets
from typing import Annotated, Literal

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, condecimal
from pydantic_settings import BaseSettings, SettingsConfigDict

from marketplace_manager import MarketplaceManager
from site_admin import SiteAdmin
from store_manager import StoreManager
from surrealdb_layer import SurrealDBLayer
from vendor_agent import VendorAgent

logger = logging.getLogger("agent_commerce")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    api_key: str | None = None
    host: str = "0.0.0.0"
    port: int = 8000
    surrealdb_url: str = "mem://"
    surrealdb_user: str | None = None
    surrealdb_password: str | None = None
    surrealdb_namespace: str = "ucp"
    surrealdb_database: str = "ecommerce"

    @property
    def auth_required(self) -> bool:
        return self.environment == "production" or bool(self.api_key)


settings = Settings()

if settings.environment == "production":
    if not settings.api_key or settings.api_key in {"change-me", "change-me-in-production"}:
        raise RuntimeError("API_KEY must be set to a strong value in production")
    if settings.surrealdb_url == "mem://":
        raise RuntimeError("SURREALDB_URL must point to a persistent database in production")

app = FastAPI(
    title="Agent-Commerce API",
    description="UCP Commerce Agents with SurrealDB",
    version="1.0.0",
)

db: SurrealDBLayer | None = None
stores: dict[str, StoreManager] = {}
vendors: dict[str, VendorAgent] = {}


class ProductCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    price: condecimal(gt=0, max_digits=12, decimal_places=2)
    store_id: str = Field(default="default", min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=5000)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    inventory: int | None = Field(default=None, ge=0)


class OrderCreate(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=200)
    line_items: list[dict] = Field(default_factory=list)
    store_id: str = Field(default="default", min_length=1, max_length=100)


class VendorProductCreate(ProductCreate):
    vendor_id: str = Field(..., min_length=1, max_length=100)


class ConversationCreate(BaseModel):
    participants: list[str] = Field(..., min_length=1, max_length=100)


class PaymentCreate(BaseModel):
    amount: condecimal(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    user_id: str = Field(..., min_length=1, max_length=200)
    idempotency_key: str = Field(..., min_length=16, max_length=200)


async def require_api_key(
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    """Require either `Authorization: Bearer ...` or `X-API-Key` when configured."""

    if not settings.auth_required:
        return

    supplied_key = x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        supplied_key = authorization.split(" ", 1)[1]

    if not supplied_key or not settings.api_key or not secrets.compare_digest(supplied_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled request error", extra={"path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.on_event("startup")
async def startup() -> None:
    global db
    db = SurrealDBLayer(
        url=settings.surrealdb_url,
        config={
            "user": settings.surrealdb_user,
            "password": settings.surrealdb_password,
            "namespace": settings.surrealdb_namespace,
            "database": settings.surrealdb_database,
        },
    )
    await db.connect()
    await db.use(settings.surrealdb_namespace, settings.surrealdb_database)
    await db.create_table("products")
    await db.create_table("orders")
    await db.create_table("agents")
    logger.info("SurrealDB connected", extra={"url": settings.surrealdb_url})


@app.get("/")
async def root():
    return {"name": "Agent-Commerce", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/ready")
async def ready():
    if db and db.connected:
        return {"status": "ready", "db": "connected"}
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not ready")


protected = Depends(require_api_key)


@app.post("/api/store/products", dependencies=[protected])
async def create_product(data: ProductCreate):
    store_key = data.store_id
    if store_key not in stores:
        stores[store_key] = StoreManager(config={})
    return await stores[store_key].create_product(data.model_dump())


@app.get("/api/store/products", dependencies=[protected])
async def list_products(store_id: str = "default"):
    store = stores.get(store_id, StoreManager(config={}))
    return await store.list_products()


@app.post("/api/store/orders", dependencies=[protected])
async def create_order(data: OrderCreate):
    store = stores.get(data.store_id, StoreManager(config={}))
    return await store.create_order(data.model_dump())


@app.get("/api/store/dashboard", dependencies=[protected])
async def dashboard(store_id: str = "default"):
    store = stores.get(store_id, StoreManager(config={}))
    return await store.get_dashboard()


@app.get("/api/admin/info", dependencies=[protected])
async def site_info():
    admin = SiteAdmin()
    return await admin.get_site_info()


@app.get("/api/admin/users", dependencies=[protected])
async def users():
    admin = SiteAdmin()
    return await admin.get_users()


@app.get("/api/admin/roles", dependencies=[protected])
async def roles():
    admin = SiteAdmin()
    return await admin.get_roles()


@app.post("/api/vendor/products", dependencies=[protected])
async def vendor_product(data: VendorProductCreate):
    vendor_id = data.vendor_id
    if vendor_id not in vendors:
        vendors[vendor_id] = VendorAgent()
    return await vendors[vendor_id].create_product(vendor_id, data.model_dump())


@app.get("/api/vendor/{vendor_id}/dashboard", dependencies=[protected])
async def vendor_dashboard(vendor_id: str):
    if vendor_id not in vendors:
        vendors[vendor_id] = VendorAgent()
    return await vendors[vendor_id].get_dashboard(vendor_id)


@app.get("/api/marketplace/settings", dependencies=[protected])
async def mp_settings():
    mgr = MarketplaceManager()
    return await mgr.get_settings()


@app.get("/api/marketplace/dashboard", dependencies=[protected])
async def mp_dashboard():
    mgr = MarketplaceManager()
    return await mgr.get_dashboard()


@app.post("/api/marketplace/conversations", dependencies=[protected])
async def create_conversation(data: ConversationCreate):
    mgr = MarketplaceManager()
    return await mgr.create_conversation(data.participants)


@app.post("/api/payments/{provider}", dependencies=[protected])
async def create_payment(provider: str, data: PaymentCreate):
    from adapters import PaymentAdapterFactory

    adapter = PaymentAdapterFactory.create(provider)
    return await adapter.create_payment(
        float(data.amount),
        data.currency,
        user_id=data.user_id,
        idempotency_key=data.idempotency_key,
    )


@app.get("/api/providers", dependencies=[protected])
async def providers():
    from adapters import PaymentAdapterFactory

    return {"providers": PaymentAdapterFactory.list_providers()}


@app.get("/api/db/health", dependencies=[protected])
async def db_health():
    if db:
        return await db.health()
    return {"status": "not_initialized"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
