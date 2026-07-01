"""Student-friendly Agent-Commerce example.

Run:
    python examples/student_basic_commerce.py

This example uses in-memory Python dictionaries only.
It avoids real payment providers, schema.org, Mercur, and advanced data models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4


OrderStatus = Literal["created", "paid", "cancelled", "refunded"]
PaymentStatus = Literal["pending", "paid", "failed", "refunded"]


@dataclass
class Product:
    id: str
    name: str
    price: float
    currency: str = "INR"
    stock: int = 0
    status: str = "active"


@dataclass
class Customer:
    id: str
    name: str
    email: str


@dataclass
class OrderItem:
    product_id: str
    quantity: int
    price: float


@dataclass
class Order:
    id: str
    customer_id: str
    items: list[OrderItem]
    total: float
    currency: str = "INR"
    status: OrderStatus = "created"


@dataclass
class Payment:
    id: str
    order_id: str
    amount: float
    currency: str
    provider: str = "mock"
    status: PaymentStatus = "pending"


@dataclass
class StudentCommerceStore:
    products: dict[str, Product] = field(default_factory=dict)
    customers: dict[str, Customer] = field(default_factory=dict)
    orders: dict[str, Order] = field(default_factory=dict)
    payments: dict[str, Payment] = field(default_factory=dict)
    agent_permissions: dict[str, set[str]] = field(default_factory=dict)

    def allow_agent(self, agent_id: str, actions: list[str]) -> None:
        self.agent_permissions[agent_id] = set(actions)

    def check_permission(self, agent_id: str, action: str) -> None:
        allowed = self.agent_permissions.get(agent_id, set())
        if action not in allowed:
            raise PermissionError(f"Agent {agent_id} cannot perform {action}")

    def create_product(self, agent_id: str, name: str, price: float, stock: int) -> Product:
        self.check_permission(agent_id, "product.create")
        product = Product(id=f"prod_{uuid4().hex[:8]}", name=name, price=price, stock=stock)
        self.products[product.id] = product
        return product

    def create_customer(self, name: str, email: str) -> Customer:
        customer = Customer(id=f"cust_{uuid4().hex[:8]}", name=name, email=email)
        self.customers[customer.id] = customer
        return customer

    def create_order(self, agent_id: str, customer_id: str, product_id: str, quantity: int) -> Order:
        self.check_permission(agent_id, "order.create")

        product = self.products[product_id]
        if product.stock < quantity:
            raise ValueError("Not enough stock")

        item = OrderItem(product_id=product.id, quantity=quantity, price=product.price)
        total = product.price * quantity
        order = Order(id=f"order_{uuid4().hex[:8]}", customer_id=customer_id, items=[item], total=total)
        self.orders[order.id] = order
        return order

    def create_payment(self, agent_id: str, order_id: str) -> Payment:
        self.check_permission(agent_id, "payment.create")

        order = self.orders[order_id]
        payment = Payment(
            id=f"pay_{uuid4().hex[:8]}",
            order_id=order.id,
            amount=order.total,
            currency=order.currency,
            provider="mock",
            status="paid",
        )

        order.status = "paid"
        for item in order.items:
            self.products[item.product_id].stock -= item.quantity

        self.payments[payment.id] = payment
        return payment


if __name__ == "__main__":
    store = StudentCommerceStore()

    agent_id = "agent_store_helper"
    store.allow_agent(agent_id, ["product.create", "order.create", "payment.create"])

    product = store.create_product(agent_id, name="Notebook", price=99, stock=50)
    customer = store.create_customer(name="Asha", email="asha@example.com")
    order = store.create_order(agent_id, customer_id=customer.id, product_id=product.id, quantity=2)
    payment = store.create_payment(agent_id, order_id=order.id)

    print("Product:", product)
    print("Customer:", customer)
    print("Order:", order)
    print("Payment:", payment)
    print("Remaining stock:", store.products[product.id].stock)
