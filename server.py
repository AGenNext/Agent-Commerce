# Agent-Commerce FastAPI Server
# Run: python3 server.py

import json
import logging
import os
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

import jwt
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
        payload = {"level": record.levelname, "logger": record.name, "message": record.getMessage(), "timestamp": self.formatTime(record, self.datefmt)}
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
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 14
    demo_auth_username: str | None = None
    demo_auth_password: str | None = None
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
        return self.environment == "production" or bool(self.api_key or self.admin_api_key or self.jwt_secret)


settings = Settings()

if settings.environment == "production":
    if not settings.api_key or settings.api_key in {"change-me", "change-me-in-production"}:
        raise RuntimeError("API_KEY must be set to a strong value in production")
    if not settings.admin_api_key or settings.admin_api_key in {"change-me", "change-me-in-production"}:
        raise RuntimeError("ADMIN_API_KEY must be set to a strong value in production")
    if not settings.jwt_secret or settings.jwt_secret in {"change-me", "change-me-in-production"}:
        raise RuntimeError("JWT_SECRET must be set to a strong value in production")
    if settings.surrealdb_url == "mem://":
        raise RuntimeError("SURREALDB_URL must point to a persistent database in production")

app = FastAPI(title="Agent-Commerce API", description="UCP Commerce Agents with SurrealDB", version="1.0.0")

db: SurrealDBLayer | None = None
stores: dict[str, StoreManager] = {}
vendors: dict[str, VendorAgent] = {}
marketplace_manager: MarketplaceManager | None = None
site_admin_manager: SiteAdmin | None = None
_request_log: dict[str, deque[float]] = defaultdict(deque)
_refresh_tokens: dict[str, dict] = {}

CORE_TABLES = [
    "products",
    "orders",
    "customers",
    "agents",
    "vendors",
    "vendor_products",
    "vendor_orders",
    "vendor_payouts",
    "vendor_messages",
    "marketplace_vendors",
    "marketplace_orders",
    "marketplace_payouts",
    "discounts",
    "returns",
    "refunds",
    "inventory_logs",
    "store_settings",
    "marketplace_settings",
    "conversations",
    "messages",
    "api_clients",
    "api_keys",
    "webhooks",
    "audit_logs",
    "site_info",
    "staff_users",
    "roles",
]


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


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=500)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=32, max_length=500)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


def _extract_bearer(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    return None


def _create_access_token(subject: str, role: str) -> str:
    if not settings.jwt_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="JWT auth is not configured")
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "role": role, "iat": now, "exp": now + timedelta(minutes=settings.access_token_minutes), "typ": "access"}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _verify_access_token(token: str) -> dict:
    if not settings.jwt_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="JWT auth is not configured")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    if payload.get("typ") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return payload


def _issue_tokens(subject: str, role: str) -> TokenResponse:
    access_token = _create_access_token(subject, role)
    refresh_token = secrets.token_urlsafe(48)
    _refresh_tokens[refresh_token] = {"sub": subject, "role": role, "expires_at": time.time() + settings.refresh_token_days * 86400}
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, expires_in=settings.access_token_minutes * 60)


def _extract_api_key(authorization: str | None, x_api_key: str | None) -> str | None:
    bearer = _extract_bearer(authorization)
    return bearer or x_api_key


def require_db() -> SurrealDBLayer:
    if not db or not db.connected:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not ready")
    return db


def get_store_manager(store_id: str) -> StoreManager:
    database = require_db()
    if store_id not in stores or stores[store_id].db is not database:
        stores[store_id] = StoreManager(db=database, config={"store_id": store_id})
    return stores[store_id]


def get_vendor_agent(vendor_id: str) -> VendorAgent:
    database = require_db()
    if vendor_id not in vendors or vendors[vendor_id].db is not database:
        vendors[vendor_id] = VendorAgent(db=database, config={"vendor_id": vendor_id})
    return vendors[vendor_id]


def get_site_admin() -> SiteAdmin:
    global site_admin_manager
    database = require_db()
    if site_admin_manager is None or site_admin_manager.db is not database:
        site_admin_manager = SiteAdmin(db=database)
    return site_admin_manager


def get_marketplace_manager() -> MarketplaceManager:
    global marketplace_manager
    database = require_db()
    if marketplace_manager is None or marketplace_manager.db is not database:
        marketplace_manager = MarketplaceManager(db=database)
    return marketplace_manager


async def require_api_key(authorization: Annotated[str | None, Header()] = None, x_api_key: Annotated[str | None, Header()] = None) -> str:
    if not settings.auth_required:
        return "development"
    bearer = _extract_bearer(authorization)
    if bearer and settings.jwt_secret:
        payload = _verify_access_token(bearer)
        return payload.get("role", "user")
    supplied_key = _extract_api_key(None, x_api_key)
    valid_user = supplied_key and settings.api_key and secrets.compare_digest(supplied_key, settings.api_key)
    valid_admin = supplied_key and settings.admin_api_key and secrets.compare_digest(supplied_key, settings.admin_api_key)
    if valid_admin:
        return "admin"
    if valid_user:
        return "user"
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid credentials")


async def require_admin(role: Annotated[str, Depends(require_api_key)]) -> None:
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin credentials required")


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
    for table in CORE_TABLES:
        await db.create_table(table)
    logger.info("SurrealDB connected and core tables initialized")


@app.post("/auth/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    if not settings.demo_auth_username or not settings.demo_auth_password:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Login is not configured")
    if not secrets.compare_digest(data.username, settings.demo_auth_username) or not secrets.compare_digest(data.password, settings.demo_auth_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    role = "admin" if data.username.lower().startswith("admin") else "user"
    return _issue_tokens(data.username, role)


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest):
    token_record = _refresh_tokens.get(data.refresh_token)
    if not token_record or token_record["expires_at"] < time.time():
        _refresh_tokens.pop(data.refresh_token, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    _refresh_tokens.pop(data.refresh_token, None)
    return _issue_tokens(token_record["sub"], token_record["role"])


@app.get("/")
async def root():
    return {"name": "Agent-Commerce", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/ready")
async def ready():
    database = require_db()
    return {"status": "ready", "db": "connected", "url": database.url}


protected = Depends(require_api_key)
admin_only = Depends(require_admin)


@app.post("/api/store/products", dependencies=[protected])
async def create_product(data: ProductCreate):
    store = get_store_manager(data.store_id)
    return await store.create_product(data.model_dump())


@app.get("/api/store/products", dependencies=[protected])
async def list_products(store_id: str = "default"):
    store = get_store_manager(store_id)
    return await store.list_products()


@app.post("/api/store/orders", dependencies=[protected])
async def create_order(data: OrderCreate):
    store = get_store_manager(data.store_id)
    return await store.create_order(data.model_dump())


@app.get("/api/store/dashboard", dependencies=[protected])
async def dashboard(store_id: str = "default"):
    store = get_store_manager(store_id)
    return await store.get_dashboard()


@app.get("/api/admin/info", dependencies=[admin_only])
async def site_info():
    admin = get_site_admin()
    return await admin.get_site_info()


@app.get("/api/admin/users", dependencies=[admin_only])
async def users():
    admin = get_site_admin()
    return await admin.get_users()


@app.get("/api/admin/roles", dependencies=[admin_only])
async def roles():
    admin = get_site_admin()
    return await admin.get_roles()


@app.post("/api/vendor/products", dependencies=[protected])
async def vendor_product(data: VendorProductCreate):
    vendor = get_vendor_agent(data.vendor_id)
    return await vendor.create_product(data.vendor_id, data.model_dump())


@app.get("/api/vendor/{vendor_id}/dashboard", dependencies=[protected])
async def vendor_dashboard(vendor_id: str):
    vendor = get_vendor_agent(vendor_id)
    return await vendor.get_dashboard(vendor_id)


@app.get("/api/marketplace/settings", dependencies=[admin_only])
async def mp_settings():
    mgr = get_marketplace_manager()
    return await mgr.get_settings()


@app.get("/api/marketplace/dashboard", dependencies=[protected])
async def mp_dashboard():
    mgr = get_marketplace_manager()
    return await mgr.get_dashboard()


@app.post("/api/marketplace/conversations", dependencies=[protected])
async def create_conversation(data: ConversationCreate):
    mgr = get_marketplace_manager()
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
    database = require_db()
    return await database.health()


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
