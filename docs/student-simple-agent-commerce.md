# Agent-Commerce: Student-Friendly Version

This guide explains Agent-Commerce in a simple way for students who are learning how modern e-commerce systems can work with AI agents, protocols, and integrations.

It intentionally avoids advanced topics such as schema.org, Mercur, marketplace-specific data models, graph databases, vector search, and enterprise governance.

## 1. What is Agent-Commerce?

Agent-Commerce is a simple e-commerce backend where an AI agent can help with common store tasks.

A normal e-commerce app lets humans do things like:

- add products
- create orders
- check inventory
- process payments
- view customers

Agent-Commerce adds an agent layer on top of this. That means software agents can call safe APIs to perform store tasks.

Example:

```text
Student asks: "Create a product called Notebook for ₹99."
Agent calls: POST /products
System stores: product name, price, stock, status
```

## 2. Main Parts

### Product Service

Stores product information.

Example product:

```json
{
  "id": "prod_001",
  "name": "Notebook",
  "price": 99,
  "currency": "INR",
  "stock": 50,
  "status": "active"
}
```

### Customer Service

Stores basic customer information.

Example customer:

```json
{
  "id": "cust_001",
  "name": "Asha",
  "email": "asha@example.com"
}
```

### Order Service

Creates orders when a customer buys products.

Example order:

```json
{
  "id": "order_001",
  "customer_id": "cust_001",
  "items": [
    {
      "product_id": "prod_001",
      "quantity": 2,
      "price": 99
    }
  ],
  "total": 198,
  "status": "created"
}
```

### Payment Service

Creates a payment request for an order.

Example payment:

```json
{
  "id": "pay_001",
  "order_id": "order_001",
  "amount": 198,
  "currency": "INR",
  "provider": "stripe",
  "status": "pending"
}
```

### Agent Service

Allows an AI agent to use approved actions.

Example allowed actions:

```json
{
  "agent_id": "agent_store_helper",
  "allowed_actions": [
    "product.create",
    "product.list",
    "order.create",
    "payment.create"
  ]
}
```

## 3. Simple Protocol View

A protocol is a common rulebook that systems follow so they can talk to each other.

In this student version, keep the protocol layer simple.

| Protocol | Simple Meaning | Use in this project |
|---|---|---|
| HTTP API | Web apps call backend endpoints | Product, order, customer, payment APIs |
| JSON | Common data format | Request and response bodies |
| UCP | Commerce action format for agents | Agent understands store actions |
| A2A | Agent-to-agent communication | One agent can ask another agent for help |
| AP2 | Agent payment authorization | Agent can request payment only with permission |
| x402 | Pay-to-access resource pattern | System can ask for payment before access |

## 4. Integrations

Integrations connect this simple backend to outside systems.

| Integration | Why it is useful |
|---|---|
| Stripe | Card payments and checkout |
| PayPal | Wallet payments |
| Shopify | Connect to an existing store |
| WooCommerce | Connect to a WordPress store |
| SurrealDB | Store products, customers, orders, and payments |
| FastAPI | Expose backend APIs |
| Docker | Run the app in a container |

For a student project, these integrations can start as mock adapters. The first goal is to understand the flow before connecting real payment providers.

## 5. Basic E-Commerce Schema

This is the smallest useful schema.

```text
Product
- id
- name
- description
- price
- currency
- stock
- status

Customer
- id
- name
- email

Order
- id
- customer_id
- items
- total
- currency
- status

OrderItem
- product_id
- quantity
- price

Payment
- id
- order_id
- amount
- currency
- provider
- status

AgentPermission
- agent_id
- allowed_actions
```

## 6. Simple API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/products` | Create a product |
| GET | `/products` | List products |
| POST | `/customers` | Create a customer |
| POST | `/orders` | Create an order |
| GET | `/orders/{id}` | View an order |
| POST | `/payments` | Create a payment |
| GET | `/payments/{id}` | Check payment status |
| POST | `/agent/actions` | Let an agent request an approved action |

## 7. Basic Flow

```text
1. Admin creates product
2. Customer places order
3. System calculates total
4. Payment request is created
5. Payment provider processes payment
6. Order status becomes paid
7. Stock is reduced
8. Agent logs what happened
```

## 8. What Students Should Build First

Start with this order:

1. Product CRUD
2. Customer creation
3. Order creation
4. Payment mock adapter
5. Agent action permission check
6. Simple logs
7. Docker run command

## 9. What Not To Add Yet

Keep the first student version small. Do not add:

- schema.org
- Mercur marketplace logic
- complex marketplace payouts
- graph traversal
- vector search
- fraud detection
- multi-currency routing
- enterprise identity
- complex governance rules

Those can come later after the basic commerce loop works.

## 10. Final Mental Model

The simple model is:

```text
Agent -> API -> Store Data -> Payment Adapter -> Order Update -> Log
```

The important lesson is not to let the agent directly change everything.

The agent should only call approved actions through APIs.

That is the foundation of safe agentic commerce.
