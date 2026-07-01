# Foundation Agent-Commerce Protocol Profile

This profile defines the minimum serious Agent-Commerce contract for learning and reference implementation work.

It uses actual protocol concepts instead of toy names:

- **UCP** for commerce actions across the shopping journey
- **AP2** for agent payment mandates and authorization
- **A2A** for agent discovery and task exchange
- **x402** for HTTP-native pay-to-access flows

This file is intentionally minimal, but it is not childish. It is a foundation profile that can grow into a production profile.

## 1. Protocol Stack

| Layer | Protocol | Purpose |
|---|---|---|
| Commerce action | UCP | Standard commerce commands such as product search, cart update, checkout, order status, refund request |
| Agent coordination | A2A | Agent discovery, Agent Cards, task delegation, structured messages |
| Payment authorization | AP2 | Payment mandate, user intent, agent delegation, spending limit, expiry, verification |
| Resource payment | x402 | HTTP 402 challenge, signed payment proof, paid resource access |
| Transport | HTTP + JSON | Request/response exchange |

## 2. UCP: Commerce Action Contract

In this profile, UCP is represented as a commerce action envelope.

A commerce action must say:

- who is acting
- what action is requested
- what resource is affected
- what input is provided
- what trace ID connects the action to audit logs

### UCP Product Create Request

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

### UCP Product Create Response

```json
{
  "ucp_version": "0.1-profile",
  "type": "commerce.action.response",
  "action": "product.create",
  "status": "accepted",
  "result": {
    "product_id": "prod_001",
    "name": "Notebook",
    "status": "active"
  },
  "trace_id": "trace_001"
}
```

### UCP Checkout Request

```json
{
  "ucp_version": "0.1-profile",
  "type": "commerce.action.request",
  "action": "checkout.create",
  "actor": {
    "type": "agent",
    "id": "agent_checkout_helper"
  },
  "resource": {
    "type": "checkout"
  },
  "input": {
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

### UCP Checkout Response

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

## 3. AP2: Agent Payment Mandate Contract

AP2 is represented here as a mandate that gives an agent limited permission to pay.

A payment mandate must include:

- user/owner granting permission
- agent receiving permission
- amount limit
- currency
- merchant or resource constraint
- expiry
- purpose
- nonce for replay protection
- signature or proof field

### AP2 Mandate Create Request

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

### AP2 Mandate Verification Response

```json
{
  "ap2_version": "0.1-profile",
  "type": "payment.mandate.verify.response",
  "mandate_id": "mandate_001",
  "status": "verified",
  "decision": "allow",
  "reason": "Mandate is active, single-use, unexpired, and bound to checkout chk_001"
}
```

### AP2 Payment Execution Request

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

### AP2 Payment Execution Response

```json
{
  "ap2_version": "0.1-profile",
  "type": "payment.execute.response",
  "payment_id": "pay_001",
  "mandate_id": "mandate_001",
  "status": "paid",
  "amount": 198,
  "currency": "INR",
  "trace_id": "trace_002"
}
```

## 4. A2A: Agent Discovery and Task Contract

A2A is represented here with a minimal Agent Card and task request.

### A2A Agent Card

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

### A2A Task Request

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

### A2A Task Response

```json
{
  "a2a_version": "0.1-profile",
  "type": "agent.task.response",
  "from_agent": "agent_checkout_helper",
  "to_agent": "agent_store_helper",
  "task": "checkout.create",
  "status": "completed",
  "result": {
    "checkout_id": "chk_001",
    "next_required_protocol": "AP2"
  },
  "trace_id": "trace_002"
}
```

## 5. x402: HTTP Payment Challenge Contract

x402 is used when an agent tries to access a paid resource and the server requires payment before access.

### Step 1: Request a paid resource

```http
GET /premium-price-feed HTTP/1.1
Host: api.example.com
Accept: application/json
```

### Step 2: Server returns HTTP 402

```http
HTTP/1.1 402 Payment Required
Content-Type: application/json

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

### Step 3: Client retries with payment proof

```http
GET /premium-price-feed HTTP/1.1
Host: api.example.com
Accept: application/json
X-PAYMENT: signed_payment_payload_placeholder
```

### Step 4: Server grants access

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-PAYMENT-RESPONSE: tx_001

{
  "resource": "/premium-price-feed",
  "data": [
    {
      "sku": "prod_001",
      "market_price": 99
    }
  ]
}
```

## 6. End-to-End Flow

```text
A2A: Store agent asks checkout agent to create checkout
UCP: Checkout agent creates checkout action
UCP: Checkout response says payment authorization is required
AP2: User grants mandate to checkout agent
AP2: Mandate is verified and payment is executed
UCP: Order status is updated to paid
Audit: The trace ID connects all steps
```

## 7. Minimum Validation Rules

A foundation implementation must reject a request when:

- the agent is not allowed to perform the UCP action
- the AP2 mandate is expired
- the AP2 mandate amount is exceeded
- the AP2 mandate merchant does not match
- the AP2 mandate is reused when `single_use` is true
- the x402 payment proof does not match the challenge
- the trace ID is missing

## 8. What This Profile Does Not Claim

This profile is not the final official UCP, AP2, A2A, or x402 specification.

It is a practical implementation profile for Agent-Commerce that uses the actual protocol roles and message shapes needed to teach and build the first working layer.

Production work should replace placeholder signatures with real cryptographic verification, real provider SDKs, replay protection, audit storage, and compliance checks.
