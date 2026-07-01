# Foundation Agent-Commerce Protocol Profile

This profile defines the minimum deployable Agent-Commerce contract.

It provides concrete payloads for:

- **UCP** commerce actions
- **AP2** payment mandates and payment execution
- **A2A** agent discovery and task exchange
- **x402** HTTP-native payment challenges
- **Audit events** bound by `trace_id`

## Protocol Flow

```text
A2A discovery
  -> UCP commerce action
  -> AP2 payment mandate
  -> AP2 payment execution or x402 challenge
  -> commerce state update
  -> audit event
```

## UCP: Commerce Action Request

```json
{
  "ucp_version": "0.1-profile",
  "type": "commerce.action.request",
  "action": "product.create",
  "actor": {
    "type": "agent",
    "id": "agent_store_helper"
  },
  "resource": {
    "type": "product"
  },
  "input": {
    "name": "Notebook",
    "description": "A simple ruled notebook",
    "price": 99,
    "currency": "INR",
    "stock": 50
  },
  "trace_id": "trace_001"
}
```

## UCP: Commerce Action Response

```json
{
  "ucp_version": "0.1-profile",
  "type": "commerce.action.response",
  "action": "checkout.create",
  "status": "requires_payment_authorization",
  "result": {
    "checkout_id": "chk_001",
    "amount": 198,
    "currency": "INR"
  },
  "next_required_protocol": "AP2",
  "trace_id": "trace_002"
}
```

## AP2: Payment Mandate

```json
{
  "ap2_version": "0.1-profile",
  "type": "payment.mandate.create",
  "mandate_id": "mandate_001",
  "grantor": {
    "type": "user",
    "id": "cust_001"
  },
  "grantee": {
    "type": "agent",
    "id": "agent_checkout_helper"
  },
  "constraints": {
    "max_amount": 198,
    "currency": "INR",
    "merchant_id": "store_001",
    "purpose": "checkout_payment",
    "expires_at": "2026-07-01T21:00:00+05:30",
    "single_use": true
  },
  "context": {
    "checkout_id": "chk_001",
    "order_preview_id": "order_preview_001"
  },
  "nonce": "nonce_001",
  "signature": "sig_placeholder_for_profile"
}
```

## AP2: Payment Execution

```json
{
  "ap2_version": "0.1-profile",
  "type": "payment.execute",
  "mandate_id": "mandate_001",
  "amount": 198,
  "currency": "INR",
  "merchant_id": "store_001",
  "checkout_id": "chk_001",
  "idempotency_key": "idem_001",
  "trace_id": "trace_002"
}
```

## A2A: Agent Card

```json
{
  "a2a_version": "0.1-profile",
  "type": "agent.card",
  "agent_id": "agent_checkout_helper",
  "name": "Checkout Helper Agent",
  "description": "Handles checkout creation and payment authorization requests.",
  "endpoint": "https://example.com/agents/checkout-helper",
  "capabilities": [
    "checkout.create",
    "payment.mandate.request",
    "order.status.read"
  ],
  "accepted_protocols": ["UCP", "AP2", "A2A"]
}
```

## A2A: Task Request

```json
{
  "a2a_version": "0.1-profile",
  "type": "agent.task.request",
  "from_agent": "agent_store_helper",
  "to_agent": "agent_checkout_helper",
  "task": "checkout.create",
  "payload": {
    "customer_id": "cust_001",
    "items": [
      {
        "product_id": "prod_001",
        "quantity": 2
      }
    ]
  },
  "trace_id": "trace_002"
}
```

## x402: Payment Challenge

```json
{
  "x402_version": "0.1-profile",
  "type": "payment.challenge",
  "resource": "/premium-price-feed",
  "amount": 1,
  "currency": "USD",
  "network": "base",
  "pay_to": "0xMerchantWallet",
  "expires_at": "2026-07-01T21:00:00+05:30",
  "challenge_id": "x402_challenge_001"
}
```

## Audit Event

```json
{
  "type": "audit.event",
  "trace_id": "trace_002",
  "event": "payment.execute.completed",
  "actor": {
    "type": "agent",
    "id": "agent_checkout_helper"
  },
  "status": "completed",
  "timestamp": "2026-07-01T21:00:01+05:30",
  "details": {
    "payment_id": "pay_001",
    "mandate_id": "mandate_001"
  }
}
```

## Minimum Enforcement Rules

A deployable implementation must reject a payload when:

- the payload does not match the schema
- the agent is not allowed to perform the UCP action
- the AP2 mandate is expired
- the AP2 amount exceeds the mandate
- the mandate merchant does not match the payment merchant
- a single-use mandate is reused
- the x402 proof does not match the challenge
- `trace_id` is missing

## Production Hardening

This profile is deployable as a validator service. For production payment execution, add:

- cryptographic signature verification
- nonce and idempotency persistence
- append-only audit storage
- provider-specific payment adapters
- rate limits
- authentication and workload identity
- OpenTelemetry traces
- SBOM and signed container images
