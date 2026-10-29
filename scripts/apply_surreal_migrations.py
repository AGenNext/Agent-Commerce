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
import sys
from pathlib import Path

# Ensure the repository root is importable when invoked as
# `python scripts/apply_surreal_migrations.py` from any working directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from surrealdb_layer import SurrealDBLayer

# Documented dependency order (see surrealql/MIGRATIONS.md). These files define
# the metamodel tables and DefinedTerms that later migrations depend on, so they
# are applied first. Any other *.surql file is applied afterwards in sorted order.
MANIFEST = [
    "schema_org_metamodel.surql",
    "schema_org_defined_terms.surql",
    "security.surql",
    "commerce_schema_org.surql",
    "commerce_actions_schema_org.surql",
    "invoice_metamodel.surql",
]


def ordered_migrations(migrations_dir: Path) -> list[Path]:
    """Return migration files in manifest order, then remaining files sorted."""
    available = {path.name: path for path in migrations_dir.glob("*.surql")}
    ordered = [available.pop(name) for name in MANIFEST if name in available]
    ordered.extend(path for _, path in sorted(available.items()))
    return ordered


async def main() -> None:
    root = Path(__file__).resolve().parents[1]
    migrations_dir = root / "surrealql"
    files = ordered_migrations(migrations_dir)

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
    skipped: list[str] = []
    try:
        for path in files:
            rel = path.relative_to(root)
            print(f"Applying {rel}")
            try:
                await db.apply_migration_file(path)
            except Exception as exc:  # best-effort: a bad file must not abort the deploy
                print(f"WARNING: skipped {rel}: {exc}")
                skipped.append(str(rel))
    finally:
        await db.close()

    if skipped:
        print(f"SurrealDB migrations applied with {len(skipped)} skipped: {', '.join(skipped)}")
    else:
        print("SurrealDB migrations applied successfully.")


if __name__ == "__main__":
    asyncio.run(main())
