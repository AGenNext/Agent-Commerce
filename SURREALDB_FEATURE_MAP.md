# SurrealDB Feature Map

This map grounds Agent-Commerce architecture decisions in SurrealDB's documented capabilities.

## Core database capabilities

SurrealDB is a multi-model database built around SurrealQL. It supports document, graph, time-series, relational, geospatial, and key-value data patterns in one engine. It also includes vector, full-text, and hybrid search, plus real-time/event-driven capabilities.

## Security and auth capabilities

SurrealDB supports multiple built-in authentication models:

- System users, created with `DEFINE USER`, scoped at root, namespace, or database level.
- Built-in RBAC for system users using built-in roles such as `OWNER`, `EDITOR`, and `VIEWER`.
- Record users using `DEFINE ACCESS ... TYPE RECORD` for application users stored as database records.
- Database-managed signup/signin logic for record users.
- JWT-based authentication with `DEFINE ACCESS ... TYPE JWT`.
- HS256, RS256, ES256-style verification models depending on access definition and key management.
- Session context through `$session`, `$token`, and `$auth`.

## Authorization and row-level security

SurrealDB enforces authorization at the database layer using `PERMISSIONS` clauses on tables and fields.

- Table permissions can independently control create, select, update, and delete.
- Field permissions can restrict select/create/update on sensitive columns.
- Row-level rules can reference `$auth`, such as `owner = $auth.id` or `$auth.role = 'admin'`.

## Capabilities sandbox

SurrealDB has capability controls for powerful query features.

- Scripting, functions, network access, guests, and arbitrary queries can be allowed or denied.
- Production deployments should deny by default and allow only required capabilities.
- Arbitrary queries can be denied for guest, record, or system users.

## What Agent-Commerce should delegate to SurrealDB

- End-user signup/signin where possible.
- User records and role fields.
- Row-level and field-level authorization.
- Session and token validation where using SurrealDB access methods.
- Audit event persistence using tables, events, or controlled writes.

## What FastAPI should keep

- HTTP routing.
- Request validation.
- Payment provider integrations.
- External commerce platform integrations.
- Agent orchestration.
- Thin handoff of identity context to SurrealDB.

## Important correction

SurrealDB has strong authentication, RBAC, permissions, session, event, and change/streaming capabilities. Audit logging should still be modeled explicitly for this app, usually as an `audit_events` table plus writes/events/change feed usage, rather than assuming a complete application-specific audit product exists out of the box.
