"""SurrealDB client adapter for Agent-Commerce.

This module is intentionally thin: SurrealDB owns schema, permissions,
auth/access rules, graph relations, search indexes, sessions, and audit tables.
Python uses this adapter to execute application workflows without duplicating
SurrealDB-native security logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from surrealdb import Surreal
except ImportError:  # pragma: no cover
    Surreal = None


class SurrealDBLayer:
    """Thin async wrapper around the official SurrealDB Python client."""

    def __init__(self, url: str = "ws://localhost:8000/rpc", config: dict | None = None):
        self.url = url
        self.config = config or {}
        self.connected = False
        self.client: Any | None = None

    async def connect(self) -> dict:
        if Surreal is None:
            raise RuntimeError("surrealdb package is not installed. Run: pip install surrealdb")

        self.client = Surreal(self.url)
        await self.client.connect()

        user = self.config.get("user")
        password = self.config.get("password")
        namespace = self.config.get("namespace", "ucp")
        database = self.config.get("database", "ecommerce")

        if user and password:
            await self.client.signin({"user": user, "pass": password})

        await self.client.use(namespace, database)
        self.connected = True
        return {"status": "connected", "url": self.url, "namespace": namespace, "database": database}

    async def close(self) -> None:
        if self.client and hasattr(self.client, "close"):
            await self.client.close()
        self.connected = False

    async def use(self, namespace: str, database: str) -> dict:
        self._require_client()
        await self.client.use(namespace, database)
        return {"namespace": namespace, "database": database}

    async def query(self, query: str, params: dict | None = None) -> Any:
        self._require_client()
        return await self.client.query(query, params or {})

    async def apply_migration_file(self, path: str | Path) -> Any:
        migration_path = Path(path)
        return await self.query(migration_path.read_text())

    async def create_table(self, name: str, schema: dict | None = None) -> Any:
        return await self.query(f"DEFINE TABLE {name} SCHEMALESS;")

    async def create(self, table: str, data: dict, id: str | None = None) -> Any:
        self._require_client()
        if id:
            return await self.client.create(f"{table}:{id}", data)
        return await self.client.create(table, data)

    async def select(self, table: str, filters: dict | None = None, limit: int = 100) -> Any:
        self._require_client()
        if not filters:
            return await self.query("SELECT * FROM type::table($table) LIMIT $limit;", {"table": table, "limit": limit})
        clauses = [f"{key} = ${key}" for key in filters]
        params = {**filters, "table": table, "limit": limit}
        return await self.query(f"SELECT * FROM type::table($table) WHERE {' AND '.join(clauses)} LIMIT $limit;", params)

    async def update(self, table: str, id: str, data: dict) -> Any:
        self._require_client()
        return await self.client.update(f"{table}:{id}", data)

    async def delete(self, table: str, id: str) -> Any:
        self._require_client()
        return await self.client.delete(f"{table}:{id}")

    async def relate(self, from_id: str, to_id: str, relation: str, data: dict | None = None) -> Any:
        return await self.query(
            "RELATE type::thing($from_id)->type::table($relation)->type::thing($to_id) CONTENT $data;",
            {"from_id": from_id, "to_id": to_id, "relation": relation, "data": data or {}},
        )

    async def search(self, table: str, term: str, fields: list[str] | None = None) -> Any:
        fields = fields or ["title", "description", "name"]
        conditions = " OR ".join(f"{field} @0@ $term" for field in fields)
        return await self.query(f"SELECT * FROM type::table($table) WHERE {conditions};", {"table": table, "term": term})

    async def vector_search(self, table: str, vector: list[float], limit: int = 10) -> Any:
        return await self.query(
            "SELECT *, vector::distance::cosine(embedding, $vector) AS distance FROM type::table($table) ORDER BY distance LIMIT $limit;",
            {"table": table, "vector": vector, "limit": limit},
        )

    async def audit(self, action: str, resource: str, metadata: dict | None = None, actor: str | None = None) -> Any:
        return await self.create(
            "audit_events",
            {"action": action, "resource": resource, "metadata": metadata or {}, "actor": actor},
        )

    async def health(self) -> dict:
        if not self.connected:
            return {"status": "disconnected", "url": self.url}
        try:
            await self.query("RETURN true;")
            return {"status": "healthy", "url": self.url}
        except Exception as exc:  # pragma: no cover
            return {"status": "unhealthy", "url": self.url, "error": str(exc)}

    async def register_agent(self, agent_data: dict) -> Any:
        return await self.create("agents", agent_data)

    async def get_agent(self, agent_id: str) -> Any:
        return await self.select("agents", {"id": agent_id}, limit=1)

    async def list_agents(self, agent_type: str | None = None) -> Any:
        return await self.select("agents", {"type": agent_type} if agent_type else None)

    def _require_client(self) -> None:
        if not self.client or not self.connected:
            raise RuntimeError("SurrealDB client is not connected")
