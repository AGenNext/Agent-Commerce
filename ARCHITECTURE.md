# Architecture Overview

## Security Model

Agent-Commerce uses SurrealDB as the source of truth for:

- User identities
- Roles and permissions
- Session records
- Refresh tokens
- Audit events
- Row-level access control

FastAPI remains a thin orchestration layer responsible for:

- HTTP routing
- Request validation
- Calling external services (payments, marketplaces)
- Agent coordination

## Request Flow

1. Client authenticates and receives a token.
2. FastAPI validates the incoming credential format.
3. SurrealDB evaluates permissions using its access controls.
4. Business logic executes only if data access is allowed.
5. Audit events are persisted to `audit_events`.

## Benefits

- Single source of truth for authorization.
- Database-enforced row-level security.
- Reduced duplicated code.
- Simpler application layer.
- Stronger auditability.
