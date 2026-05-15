"""
E-Commerce Store Manager Agent

Comprehensive agent for managing entire e-commerce operations.
Built with UCP + A2A Protocol + SurrealDB.

Sources:
- https://www.shopify.com/editions/winter2026 - Shopify MCP
- https://developer.woocommerce.com/docs/apis/rest-api/v3/ - WooCommerce API
- https://github.com/mercurjs/mercur - Mercur marketplace
- https://github.com/mercurjs/b2c-marketplace-storefront - Mercur storefront
- https://github.com/mercurjs/admin-panel - Mercur admin
- https://github.com/mercurjs/vendor-panel - Vendor panel

Capabilities:
- Store configuration
- Product management  
- Order management
- Customer management
- Inventory tracking
- Analytics & reporting
- Multi-vendor support (marketplace)
- Returns & refunds
- Platform integrations (WooCommerce, Shopify, Mercur)
"""

import uuid
from datetime import datetime, timedelta
from typing import Any


class StoreManager:
    """
    E-Commerce Store Manager.
    
    Central agent for all store operations.
    Coordinates between products, orders, customers.
    """
    
    def __init__(self, db=None, config: dict | None = None):
        self.db = db
        self.config = config or {}
        self.agent_id = f"store_mgr_{uuid.uuid4().hex[:8]}"
        self.name = config.get("store_name", "My Store")
    
    # ========== STORE CONFIGURATION ==========
    
    async def get_settings(self) -> dict:
        """Get store settings."""
        if self.db:
            result = await self.db.query("SELECT * FROM store_settings LIMIT 1")
            return result[0] if result else {"error": "Not configured"}
        
        return {
            "store_name": self.name,
            "currency": "USD",
            "timezone": "UTC",
        }
    
    async def update_settings(self, settings: dict) -> dict:
        """Update store settings."""
        if self.db:
            await self.db.create("store_settings", settings)
        return {"updated": True}
    
    # ========== PRODUCTS ==========
    
    async def create_product(self, product_data: dict) -> dict:
        """Create new product."""
        product_id = f"prod_{uuid.uuid4().hex[:12]}"
        
        product = {
            "id": product_id,
            "title": product_data.get("title"),
            "description": product_data.get("description"),
            "price": product_data.get("price"),
            "compare_at_price": product_data.get("compare_at_price"),
            "cost_per_item": product_data.get("cost_per_item"),
            "inventory": product_data.get("inventory", 0),
            "sku": product_data.get("sku", product_id),
            "barcode": product_data.get("barcode"),
            "status": product_data.get("status", "active"),
            "vendor": product_data.get("vendor"),
            "product_type": product_data.get("type"),
            "tags": product_data.get("tags", []),
            "images": product_data.get("images", []),
            "weight": product_data.get("weight"),
            "requires_shipping": product_data.get("requires_shipping", True),
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
            await self.db.merge(f"products:{product_id}", {"status": "deleted"})
        return {"id": product_id, "deleted": True}
    
    async def get_product(self, product_id: str) -> dict:
        """Get product."""
        if self.db:
            result = await self.db.query(f"SELECT * FROM products WHERE id = '{product_id}'")
            return result[0] if result else {"error": "Not found"}
        return {}
    
    async def list_products(
        self,
        limit: int = 50,
        status: str | None = None,
        vendor: str | None = None,
    ) -> dict:
        """List products."""
        query = "SELECT * FROM products WHERE status != 'deleted'"
        
        if status:
            query += f" AND status = '{status}'"
        if vendor:
            query += f" AND vendor = '{vendor}'"
        
        query += f" ORDER BY created_at DESC LIMIT {limit}"
        
        if self.db:
            result = await self.db.query(query)
            return {"products": result}
        
        return {"products": []}
    
    async def search_products(
        self, 
        search: str, 
        limit: int = 20
    ) -> dict:
        """Search products."""
        if self.db:
            result = await self.db.query(f"""
                SELECT * FROM products 
                WHERE title CONTAINS '{search}'
                OR description CONTAINS '{search}'
                OR sku CONTAINS '{search}'
                OR tags CONTAINS '{search}'
                LIMIT {limit}
            """)
            return {"products": result}
        return {"products": []}
    
    # ========== INVENTORY ==========
    
    async def update_inventory(
        self, 
        product_id: str, 
        quantity: int,
        adjustment: str = "set"
    ) -> dict:
        """Update inventory."""
        if self.db:
            product = await self.db.query(f"SELECT * FROM products WHERE id = '{product_id}'")
            if not product:
                return {"error": "Not found"}
            
            current = product[0].get("inventory", 0)
            
            if adjustment == "set":
                new_inventory = quantity
            elif adjustment == "add":
                new_inventory = current + quantity
            else:
                new_inventory = max(0, current - quantity)
            
            await self.db.merge(f"products:{product_id}", {"inventory": new_inventory})
            
            # Log inventory change
            log = {
                "product_id": product_id,
                "previous": current,
                "change": quantity,
                "new": new_inventory,
                "type": adjustment,
                "created_at": "NOW()",
            }
            await self.db.create("inventory_logs", log)
            
            return {"inventory": new_inventory}
        
        return {"inventory": quantity}
    
    async def get_low_inventory(
        self, 
        threshold: int = 10
    ) -> dict:
        """Get low inventory products."""
        if self.db:
            result = await self.db.query(f"""
                SELECT * FROM products 
                WHERE inventory <= {threshold}
                AND status = 'active'
            """)
            return {"products": result}
        return {"products": []}
    
    # ========== ORDERS ==========
    
    async def create_order(self, order_data: dict) -> dict:
        """Create order."""
        order_id = f"order_{uuid.uuid4().hex[:12]}"
        
        # Calculate totals
        line_items = order_data.get("line_items", [])
        subtotal = sum(
            item.get("price", 0) * item.get("quantity", 1) 
            for item in line_items
        )
        shipping = order_data.get("shipping", 0)
        tax = round(subtotal * 0.08, 2)  # 8% tax
        discount = order_data.get("discount", 0)
        total = subtotal + tax + shipping - discount
        
        order = {
            "id": order_id,
            "customer_id": order_data.get("customer_id"),
            "email": order_data.get("email"),
            "line_items": line_items,
            "subtotal": subtotal,
            "shipping": shipping,
            "tax": tax,
            "discount": discount,
            "total": total,
            "currency": order_data.get("currency", "USD"),
            "status": "open",
            "financial_status": "pending",
            "fulfillment_status": "unfulfilled",
            "shipping_address": order_data.get("shipping_address"),
            "billing_address": order_data.get("billing_address"),
            "note": order_data.get("note"),
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("orders", order)
            
            # Deduct inventory
            for item in line_items:
                product_id = item.get("product_id")
                qty = item.get("quantity", 1)
                if product_id:
                    await self.db.query(f"""
                        UPDATE products SET inventory = inventory - {qty}
                        WHERE id = '{product_id}'
                    """)
        
        return order
    
    async def update_order(
        self, 
        order_id: str, 
        updates: dict
    ) -> dict:
        """Update order."""
        if self.db:
            await self.db.merge(f"orders:{order_id}", updates)
        return {"id": order_id, "updated": True}
    
    async def fulfill_order(
        self, 
        order_id: str,
        tracking: dict | None = None
    ) -> dict:
        """Fulfill order."""
        fulfillment = {
            "fulfillment_status": "fulfilled",
            "fulfilled_at": "NOW()",
        }
        if tracking:
            fulfillment["tracking_company"] = tracking.get("company")
            fulfillment["tracking_number"] = tracking.get("number")
            fulfillment["tracking_url"] = tracking.get("url")
        
        if self.db:
            await self.db.merge(f"orders:{order_id}", fulfillment)
        
        return {"id": order_id, "fulfilled": True}
    
    async def cancel_order(
        self, 
        order_id: str,
        reason: str | None = None
    ) -> dict:
        """Cancel order and restore inventory."""
        if self.db:
            # Get order
            order = await self.db.query(f"SELECT * FROM orders WHERE id = '{order_id}'")
            if not order:
                return {"error": "Not found"}
            
            # Restore inventory
            for item in order[0].get("line_items", []):
                product_id = item.get("product_id")
                qty = item.get("quantity", 1)
                if product_id:
                    await self.db.query(f"""
                        UPDATE products SET inventory = inventory + {qty}
                        WHERE id = '{product_id}'
                    """)
            
            await self.db.merge(f"orders:{order_id}", {
                "status": "cancelled",
                "cancel_reason": reason,
                "cancelled_at": "NOW()",
            })
        
        return {"id": order_id, "cancelled": True}
    
    async def get_order(self, order_id: str) -> dict:
        """Get order."""
        if self.db:
            result = await self.db.query(f"SELECT * FROM orders WHERE id = '{order_id}'")
            return result[0] if result else {"error": "Not found"}
        return {}
    
    async def list_orders(
        self,
        limit: int = 50,
        status: str | None = None,
        financial_status: str | None = None,
    ) -> dict:
        """List orders."""
        query = "SELECT * FROM orders"
        conditions = []
        
        if status:
            conditions.append(f"status = '{status}'")
        if financial_status:
            conditions.append(f"financial_status = '{financial_status}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC LIMIT " + str(limit)
        
        if self.db:
            result = await self.db.query(query)
            return {"orders": result}
        return {"orders": []}
    
    # ========== CUSTOMERS ==========
    
    async def create_customer(self, customer_data: dict) -> dict:
        """Create customer."""
        customer_id = f"cust_{uuid.uuid4().hex[:12]}"
        
        customer = {
            "id": customer_id,
            "email": customer_data.get("email"),
            "first_name": customer_data.get("first_name"),
            "last_name": customer_data.get("last_name"),
            "phone": customer_data.get("phone"),
            "default_address": customer_data.get("default_address"),
            "tags": customer_data.get("tags", []),
            "note": customer_data.get("note"),
            "total_orders": 0,
            "total_spent": 0,
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("customers", customer)
        
        return customer
    
    async def get_customer(self, customer_id: str) -> dict:
        """Get customer."""
        if self.db:
            result = await self.db.query(f"SELECT * FROM customers WHERE id = '{customer_id}'")
            return result[0] if result else {"error": "Not found"}
        return {}
    
    async def update_customer(
        self, 
        customer_id: str, 
        updates: dict
    ) -> dict:
        """Update customer."""
        if self.db:
            await self.db.merge(f"customers:{customer_id}", updates)
        return {"id": customer_id, "updated": True}
    
    async def list_customers(
        self, 
        limit: int = 50,
        order_count_min: int | None = None,
    ) -> dict:
        """List customers."""
        query = "SELECT * FROM customers"
        
        if order_count_min:
            query += f" WHERE total_orders >= {order_count_min}"
        
        query += f" ORDER BY created_at DESC LIMIT {limit}"
        
        if self.db:
            result = await self.db.query(query)
            return {"customers": result}
        return {"customers": []}
    
    # ========== RETURNS & REFUNDS ==========
    
    async def create_return(
        self, 
        order_id: str,
        items: list[dict],
        reason: str
    ) -> dict:
        """Create return request."""
        return_id = f"return_{uuid.uuid4().hex[:12]}"
        
        return_request = {
            "id": return_id,
            "order_id": order_id,
            "items": items,
            "reason": reason,
            "status": "pending",
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("returns", return_request)
        
        return return_request
    
    async def process_refund(
        self, 
        order_id: str,
        amount: float | None = None,
        items: list[dict] | None = None,
        reason: str | None = None
    ) -> dict:
        """Process refund."""
        import uuid
        
        refund_id = f"ref_{uuid.uuid4().hex[:12]}"
        
        if self.db:
            order = await self.db.query(f"SELECT * FROM orders WHERE id = '{order_id}'")
            if not order:
                return {"error": "Order not found"}
            
            refund_amount = amount or order[0].get("total", 0)
            
            refund = {
                "id": refund_id,
                "order_id": order_id,
                "amount": refund_amount,
                "reason": reason,
                "status": "completed",
                "created_at": "NOW()",
            }
            await self.db.create("refunds", refund)
            
            # Update order
            await self.db.merge(f"orders:{order_id}", {
                "financial_status": "refunded",
                "refund_id": refund_id,
            })
            
            # Restore inventory
            for item in items or []:
                product_id = item.get("product_id")
                qty = item.get("quantity", 1)
                if product_id:
                    await self.db.query(f"""
                        UPDATE products SET inventory = inventory + {qty}
                        WHERE id = '{product_id}'
                    """)
        
        return {"refund_id": refund_id, "amount": refund_amount}
    
    # ========== ANALYTICS ==========
    
    async def get_dashboard(self) -> dict:
        """Get store dashboard."""
        if self.db:
            # Total products
            products = await self.db.query("SELECT COUNT(*) as count FROM products WHERE status = 'active'")
            product_count = products[0].get("count", 0) if products else 0
            
            # Orders today
            today = datetime.now().isoformat()
            orders_today = await self.db.query(f"""
                SELECT COUNT(*) as count FROM orders 
                WHERE created_at > '{today}'
            """)
            order_count = orders_today[0].get("count", 0) if orders_today else 0
            
            # Revenue today
            revenue_today = await self.db.query(f"""
                SELECT SUM(total) as revenue FROM orders 
                WHERE created_at > '{today}'
                AND financial_status = 'paid'
            """)
            revenue = revenue_today[0].get("revenue", 0) if revenue_today else 0
            
            # Low inventory count
            low_inv = await self.db.query("SELECT COUNT(*) as count FROM products WHERE inventory <= 10")
            low_count = low_inv[0].get("count", 0) if low_inv else 0
            
            return {
                "products_active": product_count,
                "orders_today": order_count,
                "revenue_today": revenue,
                "low_inventory": low_count,
            }
        
        return {}
    
    async def get_sales_report(
        self, 
        period: str = "30d",
        group_by: str = "day"
    ) -> dict:
        """Get sales report."""
        if self.db:
            result = await self.db.query(f"""
                SELECT 
                    COUNT(*) as orders,
                    SUM(total) as sales,
                    AVG(total) as avg_order,
                    SUM(tax) as tax_collected,
                    SUM(shipping) as shipping_collected
                FROM orders
                WHERE financial_status = 'paid'
                AND created_at > NOW() - '{period}'
            """)
            return result[0] if result else {}
        return {}
    
    # ========== DISCOUNTS ==========
    
    async def create_discount(
        self, 
        discount_data: dict
    ) -> dict:
        """Create discount code."""
        discount_id = f"disc_{uuid.uuid4().hex[:12]}"
        
        discount = {
            "id": discount_id,
            "code": discount_data.get("code", "").upper(),
            "type": discount_data.get("type", "percentage"),  # percentage, fixed
            "value": discount_data.get("value"),
            "min_order_value": discount_data.get("min_order_value"),
            "applies_to": discount_data.get("applies_to"),  # all, product, collection
            "product_ids": discount_data.get("product_ids", []),
            "usage_limit": discount_data.get("usage_limit"),
            "usage_count": 0,
            "starts_at": discount_data.get("starts_at"),
            "ends_at": discount_data.get("ends_at"),
            "status": "active",
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("discounts", discount)
        
        return discount
    
    async def apply_discount(
        self, 
        code: str, 
        order_total: float
    ) -> dict:
        """Apply discount to order."""
        if self.db:
            discount = await self.db.query(f"""
                SELECT * FROM discounts 
                WHERE code = '{code.upper()}'
                AND status = 'active'
            """)
            if not discount:
                return {"error": "Invalid code"}
            
            d = discount[0]
            
            # Check usage limit
            if d.get("usage_limit") and d.get("usage_count", 0) >= d["usage_limit"]:
                return {"error": "Usage limit exceeded"}
            
            # Check min order value
            if d.get("min_order_value") and order_total < d["min_order_value"]:
                return {"error": "Minimum order not met"}
            
            # Calculate discount
            if d["type"] == "percentage":
                discount_amount = order_total * (d["value"] / 100)
            else:
                discount_amount = d["value"]
            
            return {
                "discount_id": d["id"],
                "code": d["code"],
                "amount": discount_amount,
            }
        
        return {"error": "Discount not found"}
    
    # ========== AGENT CARD ==========
    
    def get_agent_card(self) -> dict:
        """Return AgentCard."""
        return {
            "name": "E-Commerce Store Manager",
            "description": "Complete store management",
            "url": f"https://agents.example.com/{self.agent_id}",
            "version": "1.0.0",
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
            },
            "skills": [
                # Store
                {"id": "store.settings", "name": "get_settings"},
                {"id": "store.dashboard", "name": "get_dashboard"},
                # Products
                {"id": "product.create", "name": "create_product"},
                {"id": "product.update", "name": "update_product"},
                {"id": "product.delete", "name": "delete_product"},
                {"id": "product.list", "name": "list_products"},
                {"id": "product.search", "name": "search_products"},
                # Inventory
                {"id": "inventory.update", "name": "update_inventory"},
                {"id": "inventory.low", "name": "get_low_inventory"},
                # Orders
                {"id": "order.create", "name": "create_order"},
                {"id": "order.fulfill", "name": "fulfill_order"},
                {"id": "order.cancel", "name": "cancel_order"},
                {"id": "order.list", "name": "list_orders"},
                # Customers
                {"id": "customer.create", "name": "create_customer"},
                {"id": "customer.list", "name": "list_customers"},
                # Returns
                {"id": "return.create", "name": "create_return"},
                {"id": "refund.process", "name": "process_refund"},
                # Analytics
                {"id": "report.sales", "name": "get_sales_report"},
                # Discounts
                {"id": "discount.create", "name": "create_discount"},
                {"id": "discount.apply", "name": "apply_discount"},
            ],
        }


# ============================================================
# E-COMMERCE PLATFORM INTEGRATIONS
# ============================================================

class WooCommerceIntegration:
    """WooCommerce integration."""
    
    def __init__(self, config: dict):
        self.config = config
        self.site_url = config.get("site_url")
        self.consumer_key = config.get("consumer_key")
        self.consumer_secret = config.get("consumer_secret")
    
    async def sync_products(self, store: StoreManager) -> dict:
        """Sync products from WooCommerce."""
        return {"synced": 0, "message": "Connect to WooCommerce API"}
    
    async def sync_orders(self, store: StoreManager) -> dict:
        """Sync orders from WooCommerce."""
        return {"synced": 0}


class ShopifyIntegration:
    """Shopify integration."""
    
    def __init__(self, config: dict):
        self.config = config
        self.shop_domain = config.get("shop_domain")
        self.access_token = config.get("access_token")
    
    async def sync_products(self, store: StoreManager) -> dict:
        """Sync products from Shopify."""
        return {"synced": 0, "message": "Connect to Shopify API"}
    
    async def sync_orders(self, store: StoreManager) -> dict:
        """Sync orders from Shopify."""
        return {"synced": 0}
    
    async def create_webhook(
        self, 
        topic: str, 
        address: str
    ) -> dict:
        """Create Shopify webhook."""
        return {"id": f"webhook_{topic}", "topic": topic}


class MercurIntegration:
    """Mercur marketplace integration."""
    
    def __init__(self, config: dict):
        self.config = config
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
    
    async def sync_products(self, store: StoreManager) -> dict:
        """Sync products from Mercur."""
        return {"synced": 0, "message": "Connect to Mercur API"}
    
    async def sync_orders(self, store: StoreManager) -> dict:
        """Sync orders from Mercur."""
        return {"synced": 0}
    
    async def sync_vendors(self, store: StoreManager) -> dict:
        """Sync vendors from Mercur."""
        return {"synced": 0}
    
    async def get_vendor_orders(
        self, 
        vendor_id: str
    ) -> dict:
        """Get vendor-specific orders."""
        return {"orders": [], "vendor_id": vendor_id}
    
    async def calculate_vendor_payout(
        self, 
        vendor_id: str,
        period_days: int = 30
    ) -> dict:
        """Calculate vendor payout."""
        return {
            "vendor_id": vendor_id,
            "gross_sales": 0,
            "platform_fee": 0,
            "payout": 0,
        }


# ============================================================
# PLATFORM FACTORY
# ============================================================

class PlatformFactory:
    """Factory for e-commerce platform integrations."""
    
    @classmethod
    def create_platform(
        cls,
        platform: str,
        config: dict
    ):
        platforms = {
            "woocommerce": WooCommerceIntegration,
            "shopify": ShopifyIntegration,
            "mercur": MercurIntegration,
        }
        
        if platform.lower() not in platforms:
            raise ValueError(f"Unknown platform: {platform}")
        
        return platforms[platform.lower()](config)


# ============================================================
# EXAMPLE USAGE
# ============================================================

async def main():
    # Create store manager
    store = StoreManager(config={"store_name": "My Shop"})
    
    # Get AgentCard
    print("Agent:", store.get_agent_card()["name"])
    
    # Create product
    product = await store.create_product({
        "title": "Wireless Headphones",
        "description": "Premium noise-cancelling headphones",
        "price": 199.99,
        "inventory": 50,
    })
    print(f"Product: {product['id']}")
    
    # Create order
    order = await store.create_order({
        "customer_id": "cust_001",
        "email": "customer@example.com",
        "line_items": [
            {"product_id": product["id"], "price": 199.99, "quantity": 1}
        ],
    })
    print(f"Order: {order['id']}, Total: ${order['total']}")
    
    # Get dashboard
    dashboard = await store.get_dashboard()
    print(f"Dashboard: {dashboard}")
    
    # Create discount
    discount = await store.create_discount({
        "code": "SAVE20",
        "type": "percentage",
        "value": 20,
    })
    print(f"Discount: {discount['code']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())