"""Apply SurrealQL migration files to SurrealDB in dependency order.

Usage:
    python scripts/apply_surreal_migrations.py

Files are applied in the MANIFEST order below (later files depend on tables,
functions, and the `ascii` analyzer created by earlier ones). Any *.surql not
in the manifest is applied afterwards in sorted order.

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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from surrealdb_layer import SurrealDBLayer

# Dependency order (mirrors surrealql/MIGRATIONS.md).
MANIFEST = [
    "schema_org_metamodel.surql",
    "schema_org_defined_terms.surql",
    "security.surql",
    "commerce_schema_org.surql",
    "commerce_actions_schema_org.surql",
    "invoice_metamodel.surql",
    "settlements_payouts.surql",
    "digital_identity_ecosystem.surql",
]


def ordered_files(migrations_dir: Path) -> tuple[list[Path], list[Path]]:
    present = {p.name: p for p in migrations_dir.glob("*.surql")}
    manifest = [present.pop(name) for name in MANIFEST if name in present]
    extras = [present[name] for name in sorted(present)]  # not in the documented chain
    return manifest, extras


async def main() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest, extras = ordered_files(root / "surrealql")

    if not manifest and not extras:
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
        # Manifest files are the documented dependency chain: fail hard if any break.
        for path in manifest:
            print(f"Applying {path.relative_to(root)}")
            await db.apply_migration_file(path)
        # Extras are not part of the documented chain; apply best-effort so a
        # broken/WIP file does not block the core deploy.
        for path in extras:
            try:
                print(f"Applying (extra) {path.relative_to(root)}")
                await db.apply_migration_file(path)
            except Exception as exc:  # noqa: BLE001
                print(f"WARNING: skipped {path.name}: {exc}")
        print("SurrealDB migrations applied successfully.")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
