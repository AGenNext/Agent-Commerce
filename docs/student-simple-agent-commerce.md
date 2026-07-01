# Foundation Agent-Commerce Overview

This document introduces the Foundation Agent-Commerce Protocol Profile.

It is not a student track. It is a minimal deployable profile for agentic commerce systems that need concrete protocol contracts without the full enterprise platform complexity.

The profile focuses on four protocol surfaces:

- **UCP**: commerce action contracts
- **AP2**: payment mandate and payment execution contracts
- **A2A**: agent discovery and task delegation contracts
- **x402**: HTTP-native payment challenge contracts

## Runtime Flow

```text
A2A discovery
  -> UCP commerce action
  -> AP2 payment mandate
  -> AP2 payment execution or x402 challenge
  -> order/payment state update
  -> audit trace
```

## Core Objects

| Object | Purpose |
|---|---|
| Agent Card | Describes what an agent can do |
| Commerce Action | Describes a UCP action request or response |
| Payment Mandate | Describes delegated payment authority |
| Payment Execution | Describes a payment attempt bound to a mandate |
| x402 Challenge | Describes a paid-resource access requirement |
| Trace ID | Connects all steps into one auditable flow |

## Deployable Service

This repo profile now includes a minimal FastAPI validator service that can:

- serve a health endpoint
- return the protocol profile
- validate protocol payloads against JSON Schema
- expose protocol examples

See:

- `protocol_service/main.py`
- `schemas/foundation-agent-commerce-protocol-profile.schema.json`
- `docs/foundation-agent-commerce-protocol-profile.md`
- `Dockerfile.protocol`
- `docker-compose.protocol.yml`
