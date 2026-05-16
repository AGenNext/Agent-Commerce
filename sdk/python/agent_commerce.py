"""
Agent-Commerce Python SDK

Install: pip install agent-commerce
Usage:
    from agent_commerce import Client
    
    client = Client(api_key="sk_...")
    product = await client.products.create(...)
"""

import aiohttp
import asyncio
from typing import Optional, Any
from datetime import datetime


class AgentCommerceError(Exception):
    """Base exception."""
    pass


class AuthenticationError(AgentCommerceError):
    """Authentication failed."""
    pass


class NotFoundError(AgentCommerceError):
    """Resource not found."""
    pass


class Client:
    """
    Main client for Agent-Commerce API.
    
    Usage:
        client = Client(api_key="sk_...")
        product = await client.products.create({"title": "Widget", "price": 29.99})
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    async def connect(self):
        """Connect to the API."""
        self._session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
    
    async def close(self):
        """Close the connection."""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make a request."""
        if not self._session:
            raise AgentCommerceError("Not connected. Call connect() first.")
        
        url = f"{self.base_url}{endpoint}"
        
        async def _do_request():
            async with self._session.request(method, url, **kwargs) as resp:
                if resp.status == 401:
                    raise AuthenticationError("Invalid API key")
                if resp.status == 404:
                    raise NotFoundError(f"Resource not found: {endpoint}")
                if resp.status >= 400:
                    text = await resp.text()
                    raise AgentCommerceError(f"Error {resp.status}: {text}")
                return await resp.json()
        
        return _do_request()
    
    @property
    def products(self):
        return ProductsManager(self)
    
    @property
    def orders(self):
        return OrdersManager(self)
    
    @property
    def payments(self):
        return PaymentsManager(self)


class ProductsManager:
    def __init__(self, client: Client):
        self._client = client
    
    async def create(self, data: dict) -> dict:
        return await self._client._request("POST", "/api/store/products", json=data)
    
    async def list(self, limit: int = 50) -> dict:
        return await self._client._request("GET", f"/api/store/products?limit={limit}")
    
    async def get(self, product_id: str) -> dict:
        return await self._client._request("GET", f"/api/store/products/{product_id}")
    
    async def update(self, product_id: str, data: dict) -> dict:
        return await self._client._request("PUT", f"/api/store/products/{product_id}", json=data)
    
    async def delete(self, product_id: str) -> dict:
        return await self._client._request("DELETE", f"/api/store/products/{product_id}")
    
    async def search(self, query: str) -> dict:
        return await self._client._request("GET", f"/api/store/products/search?q={query}")


class OrdersManager:
    def __init__(self, client: Client):
        self._client = client
    
    async def create(self, data: dict) -> dict:
        return await self._client._request("POST", "/api/store/orders", json=data)
    
    async def list(self, status: str = None) -> dict:
        url = "/api/store/orders"
        if status:
            url += f"?status={status}"
        return await self._client._request("GET", url)
    
    async def get(self, order_id: str) -> dict:
        return await self._client._request("GET", f"/api/store/orders/{order_id}")
    
    async def update(self, order_id: str, data: dict) -> dict:
        return await self._client._request("PUT", f"/api/store/orders/{order_id}", json=data)
    
    async def cancel(self, order_id: str, reason: str) -> dict:
        return await self._client._request("POST", f"/api/store/orders/{order_id}/cancel", json={"reason": reason})
    
    async def fulfill(self, order_id: str) -> dict:
        return await self._client._request("POST", f"/api/store/orders/{order_id}/fulfill")


class PaymentsManager:
    def __init__(self, client: Client):
        self._client = client
    
    async def create(self, provider: str, amount: float, currency: str = "USD", user_id: str = None) -> dict:
        return await self._client._request(
            "POST", f"/api/payments/{provider}",
            json={"amount": amount, "currency": currency, "user_id": user_id}
        )
    
    async def verify(self, provider: str, payment_id: str) -> dict:
        return await self._client._request(
            "POST", f"/api/payments/{provider}/verify",
            json={"payment_id": payment_id}
        )
    
    async def refund(self, provider: str, payment_id: str, amount: float = None) -> dict:
        data = {"payment_id": payment_id}
        if amount:
            data["amount"] = amount
        return await self._client._request(
            "POST", f"/api/payments/{provider}/refund", json=data
        )
    
    async def list_providers(self) -> dict:
        return await self._client._request("GET", "/api/providers")


class SyncClient:
    """Synchronous (blocking) client."""
    
    def __init__(self, *args, **kwargs):
        self._async = Client(*args, **kwargs)
        self._loop = asyncio.new_event_loop()
        self._connected = False
    
    def __enter__(self):
        self._loop.run_until_complete(self._async.connect())
        self._connected = True
        return self
    
    def __exit__(self, *args):
        self._loop.run_until_complete(self._async.close())
        self._loop.close()
    
    @property
    def products(self):
        return _SyncManager(self._async.products, self._loop)
    
    @property
    def orders(self):
        return _SyncManager(self._async.orders, self._loop)
    
    @property
    def payments(self):
        return _SyncManager(self._async.payments, self._loop)


class _SyncManager:
    def __init__(self, manager, loop):
        self._manager = manager
        self._loop = loop
    
    def __getattr__(self, name):
        async_method = getattr(self._manager, name)
        
        def wrapper(*args, **kwargs):
            return self._loop.run_until_complete(async_method(*args, **kwargs))
        
        return wrapper


__all__ = ["Client", "SyncClient", "AgentCommerceError", "AuthenticationError", "NotFoundError"]