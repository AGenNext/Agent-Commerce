# Agent-Commerce Documentation

Welcome to Agent-Commerce - AI-powered e-commerce agents.

## Quick Links

- [GitHub Repository](https://github.com/AGenNext/Agent-Commerce)
- [Getting Started](getting-started.md)
- [API Reference](api-reference.md)
- [SDK Guide](sdk-guide.md)
- [Payment Providers](providers.md)

## What is Agent-Commerce?

Agent-Commerce is a comprehensive framework for building autonomous e-commerce applications using:

- **UCP** - Universal Commerce Protocol
- **A2A** - Agent-to-Agent transport
- **SurrealDB** - Real-time database

## Features

- 🤖 AI Commerce Agents
- 💳 8 Payment Protocols
- 🏪 Multi-platform Store Integration
- 📊 Marketplace Management
- 🔐 Admin & Security

## Quick Example

```python
from store_manager import StoreManager

store = StoreManager(config={})
product = await store.create_product({
    "title": "AI Widget",
    "price": 29.99
})
```

---

*Built for autonomous commerce*