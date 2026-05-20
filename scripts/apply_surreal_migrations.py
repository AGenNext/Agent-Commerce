"""Apply SurrealQL migration files to SurrealDB.

Usage:
    python scripts/apply_surreal_migrations.py

Environment:
    SURREALDB_URL=ws://localhost:8000/rpc
    SURREALDB_USER=root
    SURREALDB_PASSWORD=root
    SURREALDB_NAMESPACE=ucp
    SURREALDB_DATABASE=ecommerce
"""

import asyncio
import os
from pathlib import Path

from surrealdb_layer import SurrealDBLayer


async def main() -> None:
    root = Path(__file__).resolve().parents[1]
    migrations_dir = root / "surrealql"
    files = sorted(migrations_dir.glob("*.surql"))

    if not files:
        print("No SurrealQL migration files found.")
        return

    db = SurrealDBLayer(
        url=os.getenv("SURREALDB_URL", "ws://localhost:8000/rpc"),
        config={
            "user": os.getenv("SURREALDB_USER"),
            "password": os.getenv("SURREALDB_PASSWORD"),
            "namespace": os.getenv("SURREALDB_NAMESPACE", "ucp"),
            "database": os.getenv("SURREALDB_DATABASE", "ecommerce"),
        },
    )

    await db.connect()
    try:
        for path in files:
            print(f"Applying {path.relative_to(root)}")
            await db.apply_migration_file(path)
        print("SurrealDB migrations applied successfully.")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
