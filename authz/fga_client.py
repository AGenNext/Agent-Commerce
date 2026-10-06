"""
OpenFGA client for Agent-Commerce.

A thin async wrapper over the OpenFGA HTTP API (check + write), using aiohttp
(already a project dependency) so no new runtime dependency is introduced.

Design: OpenFGA is a *complementary coarse gate*, not a replacement for
SurrealDB's row-level PERMISSIONS. When the client is disabled or unconfigured
(e.g. local dev with no OpenFGA server), `check()` returns `default_allow` so
the app still runs and SurrealDB remains the enforcing layer. Set
`default_allow=False` to fail closed in production.

Env configuration (see .env.example):
    OPENFGA_ENABLED=true
    OPENFGA_API_URL=http://localhost:8080
    OPENFGA_STORE_ID=...
    OPENFGA_MODEL_ID=...            # optional; latest model used if unset
    OPENFGA_DEFAULT_ALLOW=true      # behavior when disabled/unconfigured
"""

from __future__ import annotations

import os
from typing import Any

try:
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None


class OpenFGAClient:
    """Async OpenFGA client (check / write / batch_check)."""

    def __init__(
        self,
        api_url: str | None = None,
        store_id: str | None = None,
        model_id: str | None = None,
        enabled: bool = True,
        default_allow: bool = True,
        session: Any | None = None,
    ):
        self.api_url = (api_url or "").rstrip("/")
        self.store_id = store_id
        self.model_id = model_id
        self.enabled = enabled
        self.default_allow = default_allow
        self._session = session

    @classmethod
    def from_env(cls, env: dict | None = None) -> "OpenFGAClient":
        """Build a client from environment variables."""
        env = env or os.environ
        return cls(
            api_url=env.get("OPENFGA_API_URL", "http://localhost:8080"),
            store_id=env.get("OPENFGA_STORE_ID") or None,
            model_id=env.get("OPENFGA_MODEL_ID") or None,
            enabled=env.get("OPENFGA_ENABLED", "false").lower() in ("1", "true", "yes"),
            default_allow=env.get("OPENFGA_DEFAULT_ALLOW", "true").lower() in ("1", "true", "yes"),
        )

    @property
    def configured(self) -> bool:
        return bool(self.enabled and self.api_url and self.store_id)

    async def _request(self, path: str, payload: dict) -> dict:
        if aiohttp is None:  # pragma: no cover
            raise RuntimeError("aiohttp is not installed. Run: pip install aiohttp")
        url = f"{self.api_url}/stores/{self.store_id}{path}"
        session = self._session or aiohttp.ClientSession()
        try:
            async with session.post(url, json=payload) as resp:
                resp.raise_for_status()
                return await resp.json()
        finally:
            if self._session is None:
                await session.close()

    def _tuple_key(self, user: str, relation: str, obj: str) -> dict:
        return {"user": user, "relation": relation, "object": obj}

    async def check(self, user: str, relation: str, obj: str) -> bool:
        """Return whether `user` has `relation` on `obj`.

        Short-circuits to `default_allow` when the client is not configured,
        so the application keeps working without an OpenFGA server.
        """
        if not self.configured:
            return self.default_allow
        payload: dict = {"tuple_key": self._tuple_key(user, relation, obj)}
        if self.model_id:
            payload["authorization_model_id"] = self.model_id
        result = await self._request("/check", payload)
        return bool(result.get("allowed", False))

    async def batch_check(self, checks: list[dict]) -> list[bool]:
        """Run several checks; each item is {user, relation, object}."""
        results = []
        for c in checks:
            results.append(await self.check(c["user"], c["relation"], c["object"]))
        return results

    async def write_tuples(
        self,
        writes: list[dict] | None = None,
        deletes: list[dict] | None = None,
    ) -> dict:
        """Write and/or delete relationship tuples.

        Each tuple is {user, relation, object}. No-op (returns a skipped marker)
        when the client is not configured.
        """
        if not self.configured:
            return {"skipped": True, "reason": "openfga not configured"}
        payload: dict = {}
        if writes:
            payload["writes"] = {"tuple_keys": [self._tuple_key(**t) for t in writes]}
        if deletes:
            payload["deletes"] = {"tuple_keys": [self._tuple_key(**t) for t in deletes]}
        if self.model_id:
            payload["authorization_model_id"] = self.model_id
        if not payload.get("writes") and not payload.get("deletes"):
            return {"skipped": True, "reason": "no tuples"}
        return await self._request("/write", payload)
