"""
Shopify Product & Order Management Agent

Agent for managing products, orders, and inventory for Shopify/Mercur marketplaces.
Built with UCP + A2A Protocol + SurrealDB.
"""

import uuid
from typing import Any


class ProductAgent:
    """
    Product Management Agent.
    
    Skills:
    - Product CRUD operations
    - Inventory management
    - Order processing
    - Price updates
    """
    
    def __init__(self, db=None):
        self.db = db
        self.agent_id = f"agent_product_{uuid.uuid4().hex[:8]}"
    
    async def create_product(self, product_data: dict) -> dict:
        """Create new product."""
        import uuid
        
        product_id = f"prod_{uuid.uuid4().hex[:12]}"
        
        product = {
            "id": product_id,
            "title": product_data.get("title"),
            "description": product_data.get("description"),
            "price": product_data.get("price", 0),
            "compare_at_price": product_data.get("compare_at_price"),
            "inventory": product_data.get("inventory", 0),
            "status": "draft",
            "vendor": product_data.get("vendor"),
            "product_type": product_data.get("type"),
            "tags": product_data.get("tags", []),
            "images": product_data.get("images", []),
            "variants": product_data.get("variants", []),
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("products", product)
        
        return product
    
    async def update_product(self, product_id: str, updates: dict) -> dict:
        """Update product."""
        if self.db:
            await self.db.merge(f"products:{product_id}", updates)
        
        return {"id": product_id, "updated": True}
    
    async def delete_product(self, product_id: str) -> dict:
        """Delete product."""
        if self.db:
            await self.db.delete(f"products:{product_id}")
        
        return {"id": product_id, "deleted": True}
    
    async def get_product(self, product_id: str) -> dict:
        """Get product details."""
        if self.db:
            result = await self.db.query(f"SELECT * FROM products WHERE id = '{product_id}'")
            return result[0] if result else {"error": "Not found"}
        
        return {"id": product_id, "title": "Sample Product"}
    
    async def list_products(
        self, 
        limit: int = 50, 
        status: str | None = None
    ) -> dict:
        """List products with filters."""
        query = "SELECT * FROM products"
        if status:
            query += f" WHERE status = '{status}'"
        query += f" LIMIT {limit}"
        
        if self.db:
            result = await self.db.query(query)
            return {"products": result}
        
        return {"products": []}
    
    async def search_products(self, query: str, limit: int = 10) -> dict:
        """Search products."""
        if self.db:
            result = await self.db.query(f"""
                SELECT * FROM products 
                WHERE title CONTAINS '{query}' 
                OR description CONTAINS '{query}'
                LIMIT {limit}
            """)
            return {"products": result}
        
        return {"products": []}
    
    async def update_inventory(
        self, 
        product_id: str, 
        quantity: int,
        adjustment: str = "set"  # "set", "add", "subtract"
    ) -> dict:
        """Update inventory level."""
        if self.db:
            if adjustment == "set":
                await self.db.merge(f"products:{product_id}", {"inventory": quantity})
            elif adjustment == "add":
                await self.db.query(f"""
                    UPDATE products SET inventory = inventory + {quantity}
                    WHERE id = '{product_id}'
                """)
            elif adjustment == "subtract":
                await self.db.query(f"""
                    UPDATE products SET inventory = inventory - {quantity}
                    WHERE id = '{product_id}'
                """)
        
        return {"id": product_id, "inventory": quantity}
    
    async def update_price(
        self, 
        product_id: str, 
        price: float,
        compare_at: float | None = None
    ) -> dict:
        """Update product price."""
        updates = {"price": price}
        if compare_at:
            updates["compare_at_price"] = compare_at
        
        if self.db:
            await self.db.merge(f"products:{product_id}", updates)
        
        return {"id": product_id, "price": price}
    
    # Order Management
    async def create_order(self, order_data: dict) -> dict:
        """Create order."""
        import uuid
        
        order_id = f"order_{uuid.uuid4().hex[:12]}"
        order = {
            "id": order_id,
            "customer_id": order_data.get("customer_id"),
            "line_items": order_data.get("line_items", []),
            "subtotal": order_data.get("subtotal", 0),
            "tax": order_data.get("tax", 0),
            "shipping": order_data.get("shipping", 0),
            "total": order_data.get("total", 0),
            "currency": order_data.get("currency", "USD"),
            "status": "pending",
            "financial_status": "pending",
            "fulfillment_status": "unfulfilled",
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("orders", order)
        
        return order
    
    async def update_order_status(
        self, 
        order_id: str, 
        status: str
    ) -> dict:
        """Update order status."""
        if self.db:
            await self.db.merge(f"orders:{order_id}", {"status": status})
        
        return {"id": order_id, "status": status}
    
    async def fulfill_order(
        self, 
        order_id: str, 
        tracking_number: str | None = None
    ) -> dict:
        """Fulfill order."""
        fulfillment = {
            "fulfillment_status": "fulfilled",
            "fulfilled_at": "NOW()",
        }
        if tracking_number:
            fulfillment["tracking_number"] = tracking_number
        
        if self.db:
            await self.db.merge(f"orders:{order_id}", fulfillment)
            
            # Update inventory
            order = await self.db.query(f"SELECT * FROM orders WHERE id = '{order_id}'")
            if order:
                for item in order[0].get("line_items", []):
                    product_id = item.get("product_id")
                    quantity = item.get("quantity", 1)
                    if product_id:
                        await self.db.query(f"""
                            UPDATE products SET inventory = inventory - {quantity}
                            WHERE id = '{product_id}'
                        """)
        
        return {"id": order_id, "fulfillment_status": "fulfilled"}
    
    async def cancel_order(self, order_id: str, reason: str | None = None) -> dict:
        """Cancel order and restore inventory."""
        if self.db:
            # Get order first
            order = await self.db.query(f"SELECT * FROM orders WHERE id = '{order_id}'")
            if order:
                # Restore inventory
                for item in order[0].get("line_items", []):
                    product_id = item.get("product_id")
                    quantity = item.get("quantity", 1)
                    if product_id:
                        await self.db.query(f"""
                            UPDATE products SET inventory = inventory + {quantity}
                            WHERE id = '{product_id}'
                        """)
                
                await self.db.merge(f"orders:{order_id}", {
                    "status": "cancelled",
                    "cancel_reason": reason,
                })
        
        return {"id": order_id, "status": "cancelled"}
    
    async def get_orders(
        self, 
        limit: int = 50, 
        status: str | None = None
    ) -> dict:
        """List orders."""
        query = "SELECT * FROM orders"
        if status:
            query += f" WHERE status = '{status}'"
        query += " ORDER BY created_at DESC"
        query += f" LIMIT {limit}"
        
        if self.db:
            result = await self.db.query(query)
            return {"orders": result}
        
        return {"orders": []}
    
    async def get_order(self, order_id: str) -> dict:
        """Get order details."""
        if self.db:
            result = await self.db.query(f"SELECT * FROM orders WHERE id = '{order_id}'")
            return result[0] if result else {"error": "Not found"}
        
        return {"id": order_id}
    
    # Analytics
    async def get_sales_report(
        self, 
        period: str = "30d"
    ) -> dict:
        """Get sales report."""
        if self.db:
            result = await self.db.query(f"""
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total) as total_sales,
                    AVG(total) as avg_order_value
                FROM orders
                WHERE status = 'completed'
                AND created_at > NOW() - '{period}'
            """)
            return result[0] if result else {}
        
        return {"total_orders": 0, "total_sales": 0}
    
    async def get_low_inventory_report(
        self, 
        threshold: int = 10
    ) -> dict:
        """Get low inventory products."""
        if self.db:
            result = await self.db.query(f"""
                SELECT * FROM products 
                WHERE inventory <= {threshold}
                AND inventory > 0
            """)
            return {"products": result}
        
        return {"products": []}
    
    # AgentCard for A2A Protocol
    def get_agent_card(self) -> dict:
        """Return AgentCard for A2A discovery."""
        return {
            "name": "Product & Order Manager",
            "description": "Manages products, orders, and inventory",
            "url": f"https://agents.example.com/{self.agent_id}",
            "version": "1.0.0",
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
            },
            "skills": [
                {"id": "product.create", "name": "create_product"},
                {"id": "product.update", "name": "update_product"},
                {"id": "product.delete", "name": "delete_product"},
                {"id": "product.list", "name": "list_products"},
                {"id": "product.search", "name": "search_products"},
                {"id": "inventory.update", "name": "update_inventory"},
                {"id": "price.update", "name": "update_price"},
                {"id": "order.create", "name": "create_order"},
                {"id": "order.fulfill", "name": "fulfill_order"},
                {"id": "order.cancel", "name": "cancel_order"},
                {"id": "order.list", "name": "get_orders"},
                {"id": "report.sales", "name": "get_sales_report"},
                {"id": "report.inventory", "name": "get_low_inventory_report"},
            ],
        }


# ============================================================
# ORDER MANAGEMENT AGENT
# ============================================================

class OrderAgent:
    """
    Order Management Agent.
    
    Specialized agent for order processing,
    fulfillment, and customer service.
    """
    
    def __init__(self, db=None):
        self.db = db
        self.agent_id = f"agent_order_{uuid.uuid4().hex[:8]}"
    
    async def process_refund(
        self, 
        order_id: str, 
        items: list[dict] | None = None,
        reason: str | None = None
    ) -> dict:
        """Process refund for order."""
        import uuid
        
        refund_id = f"ref_{uuid.uuid4().hex[:12]}"
        
        # Get original order
        if self.db:
            order = await self.db.query(f"SELECT * FROM orders WHERE id = '{order_id}'")
            if not order:
                return {"error": "Order not found"}
            
            # Calculate refund amount
            refund_amount = 0
            if items:
                for item in items:
                    refund_amount += item.get("price", 0) * item.get("quantity", 1)
            else:
                refund_amount = order[0].get("total", 0)
            
            # Create refund record
            refund = {
                "id": refund_id,
                "order_id": order_id,
                "amount": refund_amount,
                "reason": reason,
                "status": "pending",
                "created_at": "NOW()",
            }
            await self.db.create("refunds", refund)
            
            # Update order
            await self.db.merge(f"orders:{order_id}", {
                "refund_id": refund_id,
                "financial_status": "refunded",
            })
        
        return {"refund_id": refund_id, "amount": refund_amount}
    
    async def send_notification(
        self, 
        order_id: str, 
        type: str,
        message: str
    ) -> dict:
        """Send order notification."""
        import uuid
        
        notif_id = f"notif_{uuid.uuid4().hex[:12]}"
        
        notification = {
            "id": notif_id,
            "order_id": order_id,
            "type": type,  # "email", "sms", "push"
            "message": message,
            "status": "sent",
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("notifications", notification)
        
        return {"id": notif_id, "status": "sent"}
    
    def get_agent_card(self) -> dict:
        """Return AgentCard."""
        return {
            "name": "Order Manager",
            "description": "Order processing and fulfillment",
            "url": f"https://agents.example.com/{self.agent_id}",
            "version": "1.0.0",
            "skills": [
                {"id": "order.refund", "name": "process_refund"},
                {"id": "order.notify", "name": "send_notification"},
                {"id": "order.fulfill", "name": "fulfill_order"},
                {"id": "order.cancel", "name": "cancel_order"},
            ],
        }


# ============================================================
# INVENTORY AGENT
# ============================================================

class InventoryAgent:
    """
    Inventory Management Agent.
    
    Monitors stock levels, triggers reorders,
    and manages warehouse operations.
    """
    
    def __init__(self, db=None):
        self.db = db
        self.agent_id = f"agent_inventory_{uuid.uuid4().hex[:8]}"
    
    async def check_levels(self) -> dict:
        """Check all inventory levels."""
        if self.db:
            result = await self.db.query("""
                SELECT * FROM products 
                ORDER BY inventory ASC
            """)
            return {"products": result}
        
        return {"products": []}
    
    async def check_low_stock(self, threshold: int = 10) -> dict:
        """Get low stock items."""
        if self.db:
            result = await self.db.query(f"""
                SELECT * FROM products 
                WHERE inventory <= {threshold}
            """)
            return {"low_stock": result}
        
        return {"low_stock": []}
    
    async def create_reorder(
        self, 
        product_id: str, 
        quantity: int
    ) -> dict:
        """Create reorder request."""
        import uuid
        
        reorder_id = f"reorder_{uuid.uuid4().hex[:12]}"
        
        reorder = {
            "id": reorder_id,
            "product_id": product_id,
            "quantity": quantity,
            "status": "pending",
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("reorders", reorder)
        
        return reorder
    
    def get_agent_card(self) -> dict:
        """Return AgentCard."""
        return {
            "name": "Inventory Manager",
            "description": "Stock monitoring and reorders",
            "url": f"https://agents.example.com/{self.agent_id}",
            "version": "1.0.0",
            "skills": [
                {"id": "inventory.check", "name": "check_levels"},
                {"id": "inventory.low", "name": "check_low_stock"},
                {"id": "inventory.reorder", "name": "create_reorder"},
            ],
        }


# ============================================================
# EXAMPLE USAGE
# ============================================================

async def main():
    # Create agents
    product_agent = ProductAgent()
    order_agent = OrderAgent()
    inventory_agent = InventoryAgent()
    
    # Get AgentCards
    print("Product Agent:")
    print(product_agent.get_agent_card()["name"])
    
    print("\nOrder Agent:")
    print(order_agent.get_agent_card()["name"])
    
    print("\nInventory Agent:")
    print(inventory_agent.get_agent_card()["name"])
    
    # Example operations
    # Create product
    product = await product_agent.create_product({
        "title": "T-Shirt",
        "price": 29.99,
        "inventory": 100,
    })
    print(f"\nCreated: {product['id']}")
    
    # Create order
    order = await product_agent.create_order({
        "customer_id": "cust_123",
        "line_items": [
            {"product_id": product["id"], "price": 29.99, "quantity": 1}
        ],
        "total": 29.99,
    })
    print(f"Order: {order['id']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())