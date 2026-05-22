"""
E-Commerce Store Manager Agent

Comprehensive agent for managing entire e-commerce operations.
Built with UCP + A2A Protocol + SurrealDB.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any


class StoreManager:
    """Central agent for store operations."""

    def __init__(self, db=None, config: dict | None = None):
        self.db = db
        self.config = config or {}
        self.agent_id = f"store_mgr_{uuid.uuid4().hex[:8]}"
        self.name = self.config.get("store_name", "My Store")

    async def get_settings(self) -> dict:
        if self.db:
            result = await self.db.query("SELECT * FROM store_settings LIMIT 1")
            return result[0] if result else {"error": "Not configured"}
        return {"store_name": self.name, "currency": "USD", "timezone": "UTC"}

    async def update_settings(self, settings: dict) -> dict:
        if self.db:
            await self.db.create("store_settings", settings)
        return {"updated": True}

    async def create_product(self, product_data: dict) -> dict:
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
        if self.db:
            await self.db.merge(f"products:{product_id}", updates)
        return {"id": product_id, "updated": True}

    async def delete_product(self, product_id: str) -> dict:
        if self.db:
            await self.db.merge(f"products:{product_id}", {"status": "deleted"})
        return {"id": product_id, "deleted": True}

    async def get_product(self, product_id: str) -> dict:
        if self.db:
            result = await self.db.query("SELECT * FROM products WHERE id = $product_id", {"product_id": product_id})
            return result[0] if result else {"error": "Not found"}
        return {}

    async def list_products(self, limit: int = 50, status: str | None = None, vendor: str | None = None) -> dict:
        return await self.search_products(search=None, status=status, vendor=vendor, limit=limit)

    async def search_products(
        self,
        search: str | None = None,
        limit: int = 20,
        status: str | None = None,
        vendor: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        in_stock: bool = False,
    ) -> dict:
        """Search products with SurrealDB-backed filters.

        Uses parameterized queries and a portable CONTAINS fallback. A future
        migration can replace the text condition with SurrealDB full-text index
        scoring without changing the API contract.
        """
        if not self.db:
            return {"products": [], "total": 0}

        limit = max(1, min(int(limit or 20), 100))
        params: dict[str, Any] = {"limit": limit}
        conditions = ["status != 'deleted'"]

        if search:
            params["search"] = search
            conditions.append(
                "(title CONTAINS $search OR description CONTAINS $search OR sku CONTAINS $search OR tags CONTAINS $search)"
            )
        if status:
            params["status"] = status
            conditions.append("status = $status")
        if vendor:
            params["vendor"] = vendor
            conditions.append("vendor = $vendor")
        if min_price is not None:
            params["min_price"] = float(min_price)
            conditions.append("price >= $min_price")
        if max_price is not None:
            params["max_price"] = float(max_price)
            conditions.append("price <= $max_price")
        if in_stock:
            conditions.append("inventory > 0")

        where_clause = " AND ".join(conditions)
        query = f"SELECT * FROM products WHERE {where_clause} ORDER BY created_at DESC LIMIT $limit"
        result = await self.db.query(query, params)
        return {"products": result, "total": len(result), "filters": {k: v for k, v in params.items() if k != "limit"}}

    async def update_inventory(self, product_id: str, quantity: int, adjustment: str = "set") -> dict:
        if self.db:
            product = await self.db.query("SELECT * FROM products WHERE id = $product_id", {"product_id": product_id})
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
            await self.db.create("inventory_logs", {"product_id": product_id, "previous": current, "change": quantity, "new": new_inventory, "type": adjustment, "created_at": "NOW()"})
            return {"inventory": new_inventory}
        return {"inventory": quantity}

    async def get_low_inventory(self, threshold: int = 10) -> dict:
        if self.db:
            result = await self.db.query("SELECT * FROM products WHERE inventory <= $threshold AND status = 'active'", {"threshold": threshold})
            return {"products": result}
        return {"products": []}

    async def create_order(self, order_data: dict) -> dict:
        order_id = f"order_{uuid.uuid4().hex[:12]}"
        line_items = order_data.get("line_items", [])
        subtotal = sum(item.get("price", 0) * item.get("quantity", 1) for item in line_items)
        shipping = order_data.get("shipping", 0)
        tax = round(subtotal * 0.08, 2)
        discount = order_data.get("discount", 0)
        total = subtotal + tax + shipping - discount
        order = {"id": order_id, "customer_id": order_data.get("customer_id"), "email": order_data.get("email"), "line_items": line_items, "subtotal": subtotal, "shipping": shipping, "tax": tax, "discount": discount, "total": total, "currency": order_data.get("currency", "USD"), "status": "open", "financial_status": "pending", "fulfillment_status": "unfulfilled", "shipping_address": order_data.get("shipping_address"), "billing_address": order_data.get("billing_address"), "note": order_data.get("note"), "created_at": "NOW()"}
        if self.db:
            await self.db.create("orders", order)
            for item in line_items:
                product_id = item.get("product_id")
                qty = item.get("quantity", 1)
                if product_id:
                    await self.db.query("UPDATE products SET inventory = inventory - $qty WHERE id = $product_id", {"qty": qty, "product_id": product_id})
        return order

    async def update_order(self, order_id: str, updates: dict) -> dict:
        if self.db:
            await self.db.merge(f"orders:{order_id}", updates)
        return {"id": order_id, "updated": True}

    async def fulfill_order(self, order_id: str, tracking: dict | None = None) -> dict:
        fulfillment = {"fulfillment_status": "fulfilled", "fulfilled_at": "NOW()"}
        if tracking:
            fulfillment.update({"tracking_company": tracking.get("company"), "tracking_number": tracking.get("number"), "tracking_url": tracking.get("url")})
        if self.db:
            await self.db.merge(f"orders:{order_id}", fulfillment)
        return {"id": order_id, "fulfilled": True}

    async def cancel_order(self, order_id: str, reason: str | None = None) -> dict:
        if self.db:
            order = await self.db.query("SELECT * FROM orders WHERE id = $order_id", {"order_id": order_id})
            if not order:
                return {"error": "Not found"}
            for item in order[0].get("line_items", []):
                product_id = item.get("product_id")
                qty = item.get("quantity", 1)
                if product_id:
                    await self.db.query("UPDATE products SET inventory = inventory + $qty WHERE id = $product_id", {"qty": qty, "product_id": product_id})
            await self.db.merge(f"orders:{order_id}", {"status": "cancelled", "cancel_reason": reason, "cancelled_at": "NOW()"})
        return {"id": order_id, "cancelled": True}

    async def get_order(self, order_id: str) -> dict:
        if self.db:
            result = await self.db.query("SELECT * FROM orders WHERE id = $order_id", {"order_id": order_id})
            return result[0] if result else {"error": "Not found"}
        return {}

    async def list_orders(self, limit: int = 50, status: str | None = None, financial_status: str | None = None) -> dict:
        query = "SELECT * FROM orders"
        conditions = []
        params: dict[str, Any] = {"limit": max(1, min(limit, 100))}
        if status:
            params["status"] = status
            conditions.append("status = $status")
        if financial_status:
            params["financial_status"] = financial_status
            conditions.append("financial_status = $financial_status")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC LIMIT $limit"
        if self.db:
            result = await self.db.query(query, params)
            return {"orders": result}
        return {"orders": []}

    async def create_customer(self, customer_data: dict) -> dict:
        customer_id = f"cust_{uuid.uuid4().hex[:12]}"
        customer = {"id": customer_id, "email": customer_data.get("email"), "first_name": customer_data.get("first_name"), "last_name": customer_data.get("last_name"), "phone": customer_data.get("phone"), "default_address": customer_data.get("default_address"), "tags": customer_data.get("tags", []), "note": customer_data.get("note"), "total_orders": 0, "total_spent": 0, "created_at": "NOW()"}
        if self.db:
            await self.db.create("customers", customer)
        return customer

    async def get_customer(self, customer_id: str) -> dict:
        if self.db:
            result = await self.db.query("SELECT * FROM customers WHERE id = $customer_id", {"customer_id": customer_id})
            return result[0] if result else {"error": "Not found"}
        return {}

    async def update_customer(self, customer_id: str, updates: dict) -> dict:
        if self.db:
            await self.db.merge(f"customers:{customer_id}", updates)
        return {"id": customer_id, "updated": True}

    async def list_customers(self, limit: int = 50, order_count_min: int | None = None) -> dict:
        query = "SELECT * FROM customers"
        params: dict[str, Any] = {"limit": max(1, min(limit, 100))}
        if order_count_min is not None:
            query += " WHERE total_orders >= $order_count_min"
            params["order_count_min"] = order_count_min
        query += " ORDER BY created_at DESC LIMIT $limit"
        if self.db:
            result = await self.db.query(query, params)
            return {"customers": result}
        return {"customers": []}

    async def create_return(self, order_id: str, items: list[dict], reason: str) -> dict:
        return_id = f"return_{uuid.uuid4().hex[:12]}"
        return_request = {"id": return_id, "order_id": order_id, "items": items, "reason": reason, "status": "pending", "created_at": "NOW()"}
        if self.db:
            await self.db.create("returns", return_request)
        return return_request

    async def process_refund(self, order_id: str, amount: float | None = None, items: list[dict] | None = None, reason: str | None = None) -> dict:
        refund_id = f"ref_{uuid.uuid4().hex[:12]}"
        refund_amount = amount or 0
        if self.db:
            order = await self.db.query("SELECT * FROM orders WHERE id = $order_id", {"order_id": order_id})
            if not order:
                return {"error": "Order not found"}
            refund_amount = amount or order[0].get("total", 0)
            await self.db.create("refunds", {"id": refund_id, "order_id": order_id, "amount": refund_amount, "reason": reason, "status": "completed", "created_at": "NOW()"})
            await self.db.merge(f"orders:{order_id}", {"financial_status": "refunded", "refund_id": refund_id})
            for item in items or []:
                product_id = item.get("product_id")
                qty = item.get("quantity", 1)
                if product_id:
                    await self.db.query("UPDATE products SET inventory = inventory + $qty WHERE id = $product_id", {"qty": qty, "product_id": product_id})
        return {"refund_id": refund_id, "amount": refund_amount}

    async def get_dashboard(self) -> dict:
        if self.db:
            today = datetime.now().isoformat()
            products = await self.db.query("SELECT COUNT(*) as count FROM products WHERE status = 'active'")
            orders_today = await self.db.query("SELECT COUNT(*) as count FROM orders WHERE created_at > $today", {"today": today})
            revenue_today = await self.db.query("SELECT SUM(total) as revenue FROM orders WHERE created_at > $today AND financial_status = 'paid'", {"today": today})
            low_inv = await self.db.query("SELECT COUNT(*) as count FROM products WHERE inventory <= 10")
            return {"products_active": products[0].get("count", 0) if products else 0, "orders_today": orders_today[0].get("count", 0) if orders_today else 0, "revenue_today": revenue_today[0].get("revenue", 0) if revenue_today else 0, "low_inventory": low_inv[0].get("count", 0) if low_inv else 0}
        return {}

    async def get_sales_report(self, period: str = "30d", group_by: str = "day") -> dict:
        if self.db:
            result = await self.db.query("""
                SELECT COUNT(*) as orders, SUM(total) as sales, AVG(total) as avg_order,
                SUM(tax) as tax_collected, SUM(shipping) as shipping_collected
                FROM orders WHERE financial_status = 'paid' AND created_at > NOW() - $period
            """, {"period": period})
            return result[0] if result else {}
        return {}

    async def create_discount(self, discount_data: dict) -> dict:
        discount_id = f"disc_{uuid.uuid4().hex[:12]}"
        discount = {"id": discount_id, "code": discount_data.get("code", "").upper(), "type": discount_data.get("type", "percentage"), "value": discount_data.get("value"), "min_order_value": discount_data.get("min_order_value"), "applies_to": discount_data.get("applies_to"), "product_ids": discount_data.get("product_ids", []), "usage_limit": discount_data.get("usage_limit"), "usage_count": 0, "starts_at": discount_data.get("starts_at"), "ends_at": discount_data.get("ends_at"), "status": "active", "created_at": "NOW()"}
        if self.db:
            await self.db.create("discounts", discount)
        return discount

    async def apply_discount(self, code: str, order_total: float) -> dict:
        if self.db:
            discount = await self.db.query("SELECT * FROM discounts WHERE code = $code AND status = 'active'", {"code": code.upper()})
            if not discount:
                return {"error": "Invalid code"}
            d = discount[0]
            if d.get("usage_limit") and d.get("usage_count", 0) >= d["usage_limit"]:
                return {"error": "Usage limit exceeded"}
            if d.get("min_order_value") and order_total < d["min_order_value"]:
                return {"error": "Minimum order not met"}
            discount_amount = order_total * (d["value"] / 100) if d["type"] == "percentage" else d["value"]
            return {"discount_id": d["id"], "code": d["code"], "amount": discount_amount}
        return {"error": "Discount not found"}

    def get_agent_card(self) -> dict:
        return {"name": "E-Commerce Store Manager", "description": "Complete store management", "url": f"https://agents.example.com/{self.agent_id}", "version": "1.0.0", "capabilities": {"streaming": False, "pushNotifications": False}, "skills": []}


class WooCommerceIntegration:
    def __init__(self, config: dict):
        self.config = config

    async def sync_products(self, store: StoreManager) -> dict:
        return {"synced": 0, "message": "Connect to WooCommerce API"}

    async def sync_orders(self, store: StoreManager) -> dict:
        return {"synced": 0}


class ShopifyIntegration:
    def __init__(self, config: dict):
        self.config = config

    async def sync_products(self, store: StoreManager) -> dict:
        return {"synced": 0, "message": "Connect to Shopify API"}

    async def sync_orders(self, store: StoreManager) -> dict:
        return {"synced": 0}

    async def create_webhook(self, topic: str, address: str) -> dict:
        return {"id": f"webhook_{topic}", "topic": topic}


class MercurIntegration:
    def __init__(self, config: dict):
        self.config = config

    async def sync_products(self, store: StoreManager) -> dict:
        return {"synced": 0, "message": "Connect to Mercur API"}

    async def sync_orders(self, store: StoreManager) -> dict:
        return {"synced": 0}

    async def sync_vendors(self, store: StoreManager) -> dict:
        return {"synced": 0}

    async def get_vendor_orders(self, vendor_id: str) -> dict:
        return {"orders": [], "vendor_id": vendor_id}

    async def calculate_vendor_payout(self, vendor_id: str, period_days: int = 30) -> dict:
        return {"vendor_id": vendor_id, "gross_sales": 0, "platform_fee": 0, "payout": 0}


class PlatformFactory:
    @classmethod
    def create_platform(cls, platform: str, config: dict):
        platforms = {"woocommerce": WooCommerceIntegration, "shopify": ShopifyIntegration, "mercur": MercurIntegration}
        if platform.lower() not in platforms:
            raise ValueError(f"Unknown platform: {platform}")
        return platforms[platform.lower()](config)
