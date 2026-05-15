"""
Marketplace Vendor Agent

Agent for managing vendor operations in multi-vendor marketplaces.
Built for Mercur-style marketplace platforms.

Capabilities:
- Vendor profile management
- Product management (per vendor)
- Order management (per vendor)
- Payout tracking
- Analytics (per vendor)
- Vendor settings
"""

import uuid
from datetime import datetime, timedelta


class VendorAgent:
    """
    Marketplace Vendor Agent.
    
    Agent for individual vendor operations.
    """
    
    def __init__(self, db=None, config: dict | None = None):
        self.db = db
        self.config = config or {}
        self.agent_id = f"vendor_{uuid.uuid4().hex[:8]}"
    
    # ========== VENDOR PROFILE ==========
    
    async def get_profile(self, vendor_id: str) -> dict:
        """Get vendor profile."""
        if self.db:
            result = await self.db.query(f"SELECT * FROM vendors WHERE id = '{vendor_id}'")
            return result[0] if result else {}
        
        return {
            "id": vendor_id,
            "name": "Vendor Store",
            "slug": "vendor-store",
            "email": "vendor@example.com",
        }
    
    async def update_profile(
        self, 
        vendor_id: str, 
        updates: dict
    ) -> dict:
        """Update vendor profile."""
        if self.db:
            await self.db.merge(f"vendors:{vendor_id}", updates)
        return {"updated": True}
    
    async def get_settings(
        self, 
        vendor_id: str
    ) -> dict:
        """Get vendor settings."""
        return {
            "vendor_id": vendor_id,
            "currency": "USD",
            "timezone": "UTC",
            "packing_slip": True,
            "automatic_fulfillment": False,
        }
    
    # ========== PRODUCTS ==========
    
    async def create_product(
        self, 
        vendor_id: str, 
        product_data: dict
    ) -> dict:
        """Create product for vendor."""
        product_id = f"prod_{uuid.uuid4().hex[:12]}"
        
        product = {
            "id": product_id,
            "vendor_id": vendor_id,
            "title": product_data.get("title"),
            "description": product_data.get("description"),
            "price": product_data.get("price"),
            "cost": product_data.get("cost"),
            "inventory": product_data.get("inventory", 0),
            "sku": product_data.get("sku"),
            "status": "active",
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("vendor_products", product)
        
        return product
    
    async def list_products(
        self, 
        vendor_id: str,
        status: str | None = None
    ) -> dict:
        """List vendor products."""
        query = f"SELECT * FROM vendor_products WHERE vendor_id = '{vendor_id}'"
        if status:
            query += f" AND status = '{status}'"
        
        if self.db:
            result = await self.db.query(query)
            return {"products": result}
        return {"products": []}
    
    # ========== ORDERS ==========
    
    async def get_orders(
        self, 
        vendor_id: str,
        status: str | None = None
    ) -> dict:
        """Get vendor orders."""
        query = f"""
            SELECT * FROM vendor_orders 
            WHERE vendor_id = '{vendor_id}'
        """
        if status:
            query += f" AND status = '{status}'"
        query += " ORDER BY created_at DESC"
        
        if self.db:
            result = await self.db.query(query)
            return {"orders": result}
        return {"orders": []}
    
    async def fulfill_order(
        self, 
        order_id: str,
        tracking: dict | None = None
    ) -> dict:
        """Fulfill vendor order."""
        updates = {
            "status": "fulfilled",
            "fulfilled_at": "NOW()",
        }
        if tracking:
            updates["tracking_company"] = tracking.get("company")
            updates["tracking_number"] = tracking.get("number")
        
        if self.db:
            await self.db.merge(f"vendor_orders:{order_id}", updates)
        
        return {"fulfilled": True}
    
    # ========== ANALYTICS ==========
    
    async def get_dashboard(
        self, 
        vendor_id: str
    ) -> dict:
        """Get vendor dashboard."""
        if self.db:
            today = datetime.now().isoformat()
            
            # Orders today
            orders = await self.db.query(f"""
                SELECT COUNT(*) as count FROM vendor_orders 
                WHERE vendor_id = '{vendor_id}'
                AND created_at > '{today}'
            """)
            
            # Revenue
            revenue = await self.db.query(f"""
                SELECT SUM(total) as revenue FROM vendor_orders 
                WHERE vendor_id = '{vendor_id}'
                AND status = 'fulfilled'
            """)
            
            # Products count
            products = await self.db.query(f"""
                SELECT COUNT(*) as count FROM vendor_products 
                WHERE vendor_id = '{vendor_id}'
                AND status = 'active'
            """)
            
            return {
                "orders_today": orders[0].get("count", 0) if orders else 0,
                "revenue": revenue[0].get("revenue", 0) if revenue else 0,
                "products": products[0].get("count", 0) if products else 0,
            }
        
        return {}
    
    async def get_sales_report(
        self, 
        vendor_id: str,
        period: str = "30d"
    ) -> dict:
        """Get sales report."""
        if self.db:
            result = await self.db.query(f"""
                SELECT 
                    COUNT(*) as orders,
                    SUM(total) as sales,
                    AVG(total) as avg_order
                FROM vendor_orders
                WHERE vendor_id = '{vendor_id}'
                AND created_at > NOW() - '{period}'
            """)
            return result[0] if result else {}
        return {}
    
    # ========== PAYOUTS ==========
    
    async def get_payout_summary(
        self, 
        vendor_id: str
    ) -> dict:
        """Get payout summary."""
        if self.db:
            pending = await self.db.query(f"""
                SELECT SUM(total) as amount FROM vendor_orders 
                WHERE vendor_id = '{vendor_id}'
                AND payout_status = 'pending'
            """)
            
            paid = await self.db.query(f"""
                SELECT SUM(amount) as amount FROM vendor_payouts
                WHERE vendor_id = '{vendor_id}'
                AND status = 'paid'
            """)
            
            return {
                "pending": pending[0].get("amount", 0) if pending else 0,
                "paid": paid[0].get("amount", 0) if paid else 0,
            }
        
        return {"pending": 0, "paid": 0}
    
    async def request_payout(
        self, 
        vendor_id: str,
        amount: float | None = None
    ) -> dict:
        """Request payout."""
        payout_id = f"payout_{uuid.uuid4().hex[:12]}"
        
        # Get pending orders total
        if self.db:
            orders = await self.db.query(f"""
                SELECT SUM(total) as total FROM vendor_orders 
                WHERE vendor_id = '{vendor_id}'
                AND payout_status = 'pending'
            """)
            
            available = orders[0].get("total", 0) if orders else 0
            payout_amount = min(amount, available) if amount else available
        
        payout = {
            "id": payout_id,
            "vendor_id": vendor_id,
            "amount": payout_amount,
            "status": "pending",
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("vendor_payouts", payout)
        
        return payout
    
    # ========== COMMUNICATION ==========
    
    async def send_message(
        self, 
        vendor_id: str,
        order_id: str | None,
        message: str
    ) -> dict:
        """Send message to admin/buyer."""
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        
        msg = {
            "id": message_id,
            "vendor_id": vendor_id,
            "order_id": order_id,
            "message": message,
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("vendor_messages", msg)
        
        return {"sent": True}
    
    # ========== AGENT CARD ==========
    
    def get_agent_card(self) -> dict:
        """Return AgentCard."""
        return {
            "name": "Marketplace Vendor Agent",
            "description": "Vendor operations management",
            "url": f"https://agents.example.com/{self.agent_id}",
            "version": "1.0.0",
            "skills": [
                {"id": "vendor.profile", "name": "get_profile"},
                {"id": "vendor.settings", "name": "get_settings"},
                {"id": "product.create", "name": "create_product"},
                {"id": "product.list", "name": "list_products"},
                {"id": "order.list", "name": "get_orders"},
                {"id": "order.fulfill", "name": "fulfill_order"},
                {"id": "dashboard", "name": "get_dashboard"},
                {"id": "report.sales", "name": "get_sales_report"},
                {"id": "payout.summary", "name": "get_payout_summary"},
                {"id": "payout.request", "name": "request_payout"},
                {"id": "message.send", "name": "send_message"},
            ],
        }


# ============================================================
# VENDOR PANEL (Admin view for vendors)
# ============================================================

class VendorPanel:
    """
    Vendor Panel Agent -Admin view for managing all vendors.
    """
    
    def __init__(self, db=None):
        self.db = db
        self.agent_id = f"vendor_panel_{uuid.uuid4().hex[:8]}"
    
    async def get_all_vendors(
        self, 
        status: str | None = None
    ) -> dict:
        """Get all vendors."""
        query = "SELECT * FROM vendors"
        if status:
            query += f" WHERE status = '{status}'"
        
        if self.db:
            result = await self.db.query(query)
            return {"vendors": result}
        return {"vendors": []}
    
    async def approve_vendor(
        self, 
        vendor_id: str
    ) -> dict:
        """Approve vendor."""
        if self.db:
            await self.db.merge(f"vendors:{vendor_id}", {
                "status": "approved",
                "approved_at": "NOW()",
            })
        return {"approved": True}
    
    async def reject_vendor(
        self, 
        vendor_id: str,
        reason: str
    ) -> dict:
        """Reject vendor."""
        if self.db:
            await self.db.merge(f"vendors:{vendor_id}", {
                "status": "rejected",
                "rejection_reason": reason,
                "rejected_at": "NOW()",
            })
        return {"rejected": True}
    
    async def get_vendor_orders(
        self, 
        vendor_id: str
    ) -> dict:
        """Get orders for specific vendor."""
        if self.db:
            result = await self.db.query(f"""
                SELECT * FROM vendor_orders 
                WHERE vendor_id = '{vendor_id}'
                ORDER BY created_at DESC
            """)
            return {"orders": result}
        return {"orders": []}
    
    async def calculate_payout(
        self, 
        vendor_id: str,
        period_days: int = 30
    ) -> dict:
        """Calculate vendor payout."""
        if self.db:
            sales = await self.db.query(f"""
                SELECT 
                    SUM(total) as gross,
                    COUNT(*) as orders
                FROM vendor_orders
                WHERE vendor_id = '{vendor_id}'
                AND created_at > NOW() - '{period_days}d'
                AND status = 'fulfilled'
            """)
            
            gross = sales[0].get("gross", 0) if sales else 0
            platform_fee = gross * 0.10  # 10% fee
            payout = gross - platform_fee
            
            return {
                "vendor_id": vendor_id,
                "gross_sales": gross,
                "platform_fee": platform_fee,
                "payout": payout,
                "orders": sales[0].get("orders", 0),
                "period_days": period_days,
            }
        
        return {}
    
    def get_agent_card(self) -> dict:
        """Return AgentCard."""
        return {
            "name": "Vendor Panel Admin",
            "description": "Manage marketplace vendors",
            "url": f"https://agents.example.com/{self.agent_id}",
            "version": "1.0.0",
            "skills": [
                {"id": "vendor.list", "name": "get_all_vendors"},
                {"id": "vendor.approve", "name": "approve_vendor"},
                {"id": "vendor.reject", "name": "reject_vendor"},
                {"id": "vendor.orders", "name": "get_vendor_orders"},
                {"id": "vendor.payout", "name": "calculate_payout"},
            ],
        }


# ============================================================
# EXAMPLE
# ============================================================

async def main():
    vendor = VendorAgent()
    panel = VendorPanel()
    
    print("Vendor Agent:", vendor.get_agent_card()["name"])
    print("Panel Agent:", panel.get_agent_card()["name"])
    
    # Get dashboard
    dash = await vendor.get_dashboard("vendor_001")
    print("Dashboard:", dash)
    
    # Create product
    product = await vendor.create_product("vendor_001", {
        "title": "Test Product",
        "price": 29.99,
        "inventory": 10,
    })
    print("Product:", product["id"])


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())