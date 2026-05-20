# Authentication Guide

## API Keys

- `API_KEY`: standard access
- `ADMIN_API_KEY`: administrative access

Send either:

```http
Authorization: Bearer <api-key>
```

or

```http
X-API-Key: <api-key>
```

## JWT Authentication

The recommended next step is to issue short-lived JWTs to end users after validating credentials with your identity provider.

Suggested claims:
- `sub`: user identifier
- `role`: user/admin
- `exp`: expiration timestamp
- `iat`: issued-at timestamp

Suggested flow:
1. User authenticates with your identity provider.
2. Backend issues a JWT.
3. Client sends `Authorization: Bearer <jwt>`.
4. API validates signature and role claims.

## Token Rotation

- Access tokens: 15 minutes
- Refresh tokens: 7-30 days
- Rotate signing secrets regularly

## Production Recommendations

- Store secrets in a managed secret store.
- Use asymmetric signing (RS256) for distributed systems.
- Revoke refresh tokens on logout.
- Record audit events for privileged actions.
