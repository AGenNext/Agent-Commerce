# Agent-Commerce FastAPI Server
# Run: python3 server.py

import json
import logging
import os
import secrets
import time
from collections import defaultdict, deque
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


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, self.datefmt),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging() -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), handlers=[handler], force=True)
    return logging.getLogger("agent_commerce")


logger = configure_logging()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    api_key: str | None = None
    admin_api_key: str | None = None
    host: str = "0.0.0.0"
    port: int = 8000
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60
    surrealdb_url: str = "mem://"
    surrealdb_user: str | None = None
    surrealdb_password: str | None = None
    surrealdb_namespace: str = "ucp"
    surrealdb_database: str = "ecommerce"

    @property
    def auth_required(self) -> bool:
        return self.environment == "production" or bool(self.api_key or self.admin_api_key)


settings = Settings()

if settings.environment == "production":
    if not settings.api_key or settings.api_key in {"change-me", "change-me-in-production"}:
        raise RuntimeError("API_KEY must be set to a strong value in production")
    if not settings.admin_api_key or settings.admin_api_key in {"change-me", "change-me-in-production"}:
        raise RuntimeError("ADMIN_API_KEY must be set to a strong value in production")
    if settings.surrealdb_url == "mem://":
        raise RuntimeError("SURREALDB_URL must point to a persistent database in production")

app = FastAPI(title="Agent-Commerce API", description="UCP Commerce Agents with SurrealDB", version="1.0.0")

db: SurrealDBLayer | None = None
stores: dict[str, StoreManager] = {}
vendors: dict[str, VendorAgent] = {}
_request_log: dict[str, deque[float]] = defaultdict(deque)


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


def _extract_api_key(authorization: str | None, x_api_key: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    return x_api_key


async def require_api_key(
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header()] = None,
) -> str:
    if not settings.auth_required:
        return "development"
    supplied_key = _extract_api_key(authorization, x_api_key)
    valid_user = supplied_key and settings.api_key and secrets.compare_digest(supplied_key, settings.api_key)
    valid_admin = supplied_key and settings.admin_api_key and secrets.compare_digest(supplied_key, settings.admin_api_key)
    if valid_admin:
        return "admin"
    if valid_user:
        return "user"
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key")


async def require_admin(role: Annotated[str, Depends(require_api_key)]) -> None:
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin API key required")


@app.middleware("http")
async def rate_limit_and_headers(request: Request, call_next):
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    bucket = _request_log[client]
    while bucket and now - bucket[0] > settings.rate_limit_window_seconds:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_requests:
        return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": "Rate limit exceeded"})
    bucket.append(now)

    started = time.monotonic()
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    logger.info(json.dumps({"method": request.method, "path": request.url.path, "status_code": response.status_code, "duration_ms": round((time.monotonic() - started) * 1000, 2)}))
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled request error")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})


@app.on_event("startup")
async def startup() -> None:
    global db
    db = SurrealDBLayer(url=settings.surrealdb_url, config={"user": settings.surrealdb_user, "password": settings.surrealdb_password, "namespace": settings.surrealdb_namespace, "database": settings.surrealdb_database})
    await db.connect()
    await db.use(settings.surrealdb_namespace, settings.surrealdb_database)
    await db.create_table("products")
    await db.create_table("orders")
    await db.create_table("agents")
    logger.info("SurrealDB connected")


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
admin_only = Depends(require_admin)


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


@app.get("/api/admin/info", dependencies=[admin_only])
async def site_info():
    admin = SiteAdmin()
    return await admin.get_site_info()


@app.get("/api/admin/users", dependencies=[admin_only])
async def users():
    admin = SiteAdmin()
    return await admin.get_users()


@app.get("/api/admin/roles", dependencies=[admin_only])
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


@app.get("/api/marketplace/settings", dependencies=[admin_only])
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
    return await adapter.create_payment(float(data.amount), data.currency, user_id=data.user_id, idempotency_key=data.idempotency_key)


@app.get("/api/providers", dependencies=[protected])
async def providers():
    from adapters import PaymentAdapterFactory

    return {"providers": PaymentAdapterFactory.list_providers()}


@app.get("/api/db/health", dependencies=[admin_only])
async def db_health():
    if db:
        return await db.health()
    return {"status": "not_initialized"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
