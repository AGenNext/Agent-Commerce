# Core Stabilization Implementation Plan

Tracks issue #8 and breaks the first production-hardening pass into reviewable work.

## First PR: DB-backed API managers (#9)

### Changes
- Add a `require_db()` helper in `server.py` that returns a connected `SurrealDBLayer` or raises HTTP 503.
- Add manager factory helpers:
  - `get_store_manager(store_id)`
  - `get_vendor_agent(vendor_id)`
  - `get_site_admin()`
  - `get_marketplace_manager()`
- Pass the shared DB into each manager instead of creating non-persistent managers.
- Initialize all core schemaless tables during startup.

### Startup tables
- products
- orders
- customers
- agents
- vendors
- vendor_products
- vendor_orders
- vendor_payouts
- vendor_messages
- marketplace_vendors
- marketplace_orders
- marketplace_payouts
- discounts
- returns
- refunds
- inventory_logs
- store_settings
- marketplace_settings
- conversations
- messages
- api_clients
- api_keys
- webhooks
- audit_logs
- site_info
- staff_users
- roles

### Acceptance criteria
- Product creation persists through SurrealDB.
- Product listing reads from the same DB-backed manager.
- Order creation persists through SurrealDB.
- Dashboard reads DB-backed counts.
- Admin, vendor, and marketplace routes no longer create disconnected managers.

## Second PR: Safe SurrealDB queries (#10)

Replace f-string query interpolation with parameterized `db.query(sql, params)` calls.

## Third PR: Complete product/order CRUD API (#11)

Expose full product/order lifecycle endpoints with Pydantic models and tests.
