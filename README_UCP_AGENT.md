# UCP Agent

An AI agent implementation based on the [Universal Commerce Protocol (UCP)](https://ucp.dev) with [A2A Protocol](https://a2a-protocol.org) transport and [SurrealDB](https://surrealdb.com) backend for retail/ecommerce.

## Overview

This agent implements UCP commerce capabilities with SurrealDB-powered retail features:

- **A2A Protocol Support**: Agent-to-agent discovery via AgentCard
- **UCP Commerce**: discover, checkout, payment, refund
- **Product Search**: Vector + graph similarity search
- **AI Recommendations**: Personalized product suggestions
- **Dynamic Pricing**: Real-time pricing based on inventory/demand
- **Fraud Detection**: Graph-based anomaly detection
- **Visual Intelligence**: SurrealML image analysis
- **Trending Analytics**: Real-time product analytics

## Protocols & Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Agent Protocol | UCP | 2025-01-01 |
| Agent Transport | A2A | 2024-09-09 |
| Database | SurrealDB | Latest |

## Installation

```bash
pip install openhands aiohttp surrealdb
```

## Usage

### Initialize with SurrealDB

```python
from ucp_agent import UCPAgent
import os

agent = UCPAgent(
    llm_api_key=os.environ["LLM_API_KEY"],
    surreal_url="mem://"  # In-memory for dev, or "ws://localhost:8000"
)
await agent.connect_db()
```

### A2A AgentCard

```python
agent_card = agent.get_agent_card()
print(agent_card["capabilities"]["skills"])
```

### Retail Actions

```python
import asyncio

async def main():
    # Search products
    result = await agent.execute_commerce_action("search", {
        "query": "headphones"
    })
    
    # AI Recommendations
    result = await agent.execute_commerce_action("recommendations", {
        "user_id": "user_001"
    })
    
    # Dynamic Pricing
    result = await agent.execute_commerce_action("dynamic_pricing", {
        "product_id": "prod_001",
        "user_id": "user_001"
    })
    
    # Fraud Detection
    result = await agent.execute_commerce_action("fraud_detection", {
        "user_id": "user_001",
        "amount": 500.00
    })

asyncio.run(main())
```

## SurrealDB Retail Features

### Schema

- **products**: id, name, description, price, category, embedding, inventory
- **users**: id, email, name, preferences, purchase_history
- **transactions**: id, user_id, amount, status (for fraud detection)
- **orders**: id, user_id, items, total, status

### Capabilities

| Feature | Description |
|---------|-------------|
| **Recommendations** | Graph + vector search for personalized suggestions |
| **Dynamic Pricing** | Inventory, demand, and segment-based pricing |
| **Fraud Detection** | Real-time graph analytics for anomaly detection |
| **Visual Intelligence** | SurrealML image classification |
| **Trending** | Time-series analytics for popular products |
| **Semantic Search** | AI-powered product matching |

## Environment Variables

- `LLM_API_KEY` - Your LLM API key (required)
- `LLM_BASE_MODEL` - Model to use (default: openai/gpt-4o-mini)

## A2A Skills

| Skill | Category | Description |
|-------|----------|-------------|
| `discover` | commerce | Discover UCP services |
| `checkout` | commerce | Initiate checkout |
| `payment` | commerce | Process payment |
| `refund` | commerce | Process refund |
| `search` | retail | Product search (full-text/vector) |
| `recommendations` | retail | AI recommendations |
| `dynamic_pricing` | retail | Real-time pricing |
| `fraud_detection` | retail | Graph fraud analysis |
| `image_analysis` | retail | SurrealML visuals |
| `trending` | retail | Analytics |
| `register` | auth | Create user account |
| `login` | auth | Authenticate user |
| `logout` | auth | End session |
| `mfa` | auth | Enable MFA |
| `api_key` | auth | Create API key |
| `add_payment_method` | payment | Add payment method |
| `checkout` | payment | Create checkout session |
| `process_payment` | payment | Process payment |
| `refund` | payment | Refund payment |
| `payment_history` | payment | Get payment history |

## SurrealDB Multi-Model Features

| Feature | Model | Description |
|---------|-------|-------------|
| Products | Relational+Document | Table with nested fields |
| Users | Document | JSON profiles |
| Relationships | Graph | User-Product edges |
| Price History | Time-series | Temporal data |
| Sessions | Document | Auth sessions |
| API Keys | Document | Access control |
| Live Queries | Real-time | Push updates |

## Related

- [Universal Commerce Protocol (UCP)](https://ucp.dev)
- [A2A Protocol](https://a2a-protocol.org)
- [SurrealDB](https://surrealdb.com)
- [UCP Specification](https://github.com/Universal-Commerce-Protocol/ucp)