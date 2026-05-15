"""
E-Commerce Site Admin Agent

Comprehensive admin agent for managing e-commerce site operations.
Built with UCP + A2A Protocol + SurrealDB.

Responsibilities:
- Site configuration & settings
- User & role management
- Theme & appearance
- Site navigation & pages
- SEO settings
- Email notifications
- Security & access control
- Audit logs
- Site backups
- API keys management
"""

import uuid
from datetime import datetime, timedelta
from typing import Any


class SiteAdmin:
    """
    E-Commerce Site Admin.
    
    Main agent for site-wide administration.
    """
    
    def __init__(self, db=None, config: dict | None = None):
        self.db = db
        self.config = config or {}
        self.agent_id = f"site_admin_{uuid.uuid4().hex[:8]}"
    
    # ========== SITE SETTINGS ==========
    
    async def get_site_info(self) -> dict:
        """Get site information."""
        if self.db:
            result = await self.db.query("SELECT * FROM site_info LIMIT 1")
            return result[0] if result else {}
        
        return {
            "name": "My E-Commerce Store",
            "domain": "store.example.com",
            "currency": "USD",
            "timezone": "UTC",
            "email": "admin@example.com",
        }
    
    async def update_site_info(self, info: dict) -> dict:
        """Update site information."""
        if self.db:
            await self.db.create("site_info", info)
        return {"updated": True}
    
    async def get_general_settings(self) -> dict:
        """Get general settings."""
        return {
            "store_title": "My Store",
            "store_email": "admin@store.com",
            "password_requirements": {
                "min_length": 8,
                "require_special": True,
            },
            "account_options": {
                "allow_guest_checkout": True,
                "require_email_verification": False,
            },
        }
    
    async def update_general_settings(self, settings: dict) -> dict:
        """Update general settings."""
        if self.db:
            await self.db.create("general_settings", settings)
        return {"updated": True}
    
    # ========== LEGAL SETTINGS ==========
    
    async def get_legal_settings(self) -> dict:
        """Get legal settings."""
        return {
            "terms_of_service": {
                "enabled": True,
                "page_id": None,
            },
            "privacy_policy": {
                "enabled": True,
                "page_id": None,
            },
            "refund_policy": {
                "enabled": True,
                "days": 30,
            },
        }
    
    async def update_legal_settings(self, settings: dict) -> dict:
        """Update legal settings."""
        if self.db:
            await self.db.create("legal_settings", settings)
        return {"updated": True}
    
    # ========== SHIPPING SETTINGS ==========
    
    async def get_shipping_zones(self) -> dict:
        """Get shipping zones."""
        if self.db:
            result = await self.db.query("SELECT * FROM shipping_zones")
            return {"zones": result}
        return {"zones": []}
    
    async def create_shipping_zone(
        self, 
        name: str, 
        regions: list[str]
    ) -> dict:
        """Create shipping zone."""
        zone_id = f"zone_{uuid.uuid4().hex[:12]}"
        
        zone = {
            "id": zone_id,
            "name": name,
            "regions": regions,
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("shipping_zones", zone)
        
        return zone
    
    async def add_shipping_rate(
        self, 
        zone_id: str, 
        rate_data: dict
    ) -> dict:
        """Add shipping rate to zone."""
        rate_id = f"rate_{uuid.uuid4().hex[:12]}"
        
        rate = {
            "id": rate_id,
            "zone_id": zone_id,
            "name": rate_data.get("name"),
            "price": rate_data.get("price"),
            "min_order_value": rate_data.get("min_order_value"),
            "is_free": rate_data.get("is_free", False),
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("shipping_rates", rate)
        
        return rate
    
    # ========== PAYMENT SETTINGS ==========
    
    async def get_payment_settings(self) -> dict:
        """Get payment settings."""
        return {
            "payment_gateways": [],
            "currency": "USD",
            "supported_currencies": ["USD", "EUR", "GBP"],
        }
    
    async def enable_gateway(
        self, 
        gateway: str, 
        config: dict
    ) -> dict:
        """Enable payment gateway."""
        gateway_id = f"gw_{gateway}_{uuid.uuid4().hex[:8]}"
        
        settings = {
            "id": gateway_id,
            "gateway": gateway,
            "config": config,
            "enabled": True,
            "test_mode": config.get("test_mode", True),
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("payment_gateways", settings)
        
        return settings
    
    # ========== TAX SETTINGS ==========
    
    async def get_tax_settings(self) -> dict:
        """Get tax settings."""
        return {
            "taxes": [],
            "tax_included": False,
            "tax_shipping": False,
        }
    
    async def create_tax_rate(
        self, 
        rate_data: dict
    ) -> dict:
        """Create tax rate."""
        rate_id = f"tax_{uuid.uuid4().hex[:12]}"
        
        rate = {
            "id": rate_id,
            "name": rate_data.get("name"),
            "rate": rate_data.get("rate"),  # percentage
            "country": rate_data.get("country"),
            "region": rate_data.get("region"),
            "postcode": rate_data.get("postcode"),
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("tax_rates", rate)
        
        return rate
    
    # ========== USER MANAGEMENT ==========
    
    async def create_user(
        self, 
        user_data: dict
    ) -> dict:
        """Create staff user."""
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        
        user = {
            "id": user_id,
            "email": user_data.get("email"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "role": user_data.get("role", "staff"),
            "status": "active",
            "permissions": user_data.get("permissions", []),
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("staff_users", user)
        
        return user
    
    async def get_users(
        self, 
        role: str | None = None
    ) -> dict:
        """Get staff users."""
        query = "SELECT * FROM staff_users"
        if role:
            query += f" WHERE role = '{role}'"
        
        if self.db:
            result = await self.db.query(query)
            return {"users": result}
        return {"users": []}
    
    async def update_user_permissions(
        self, 
        user_id: str, 
        permissions: list[str]
    ) -> dict:
        """Update user permissions."""
        if self.db:
            await self.db.merge(f"staff_users:{user_id}", {
                "permissions": permissions,
                "updated_at": "NOW()",
            })
        return {"updated": True}
    
    async def deactivate_user(
        self, 
        user_id: str
    ) -> dict:
        """Deactivate user."""
        if self.db:
            await self.db.merge(f"staff_users:{user_id}", {
                "status": "inactive",
                "deactivated_at": "NOW()",
            })
        return {"deactivated": True}
    
    # ========== ROLES & PERMISSIONS ==========
    
    async def get_roles(self) -> dict:
        """Get user roles."""
        return {
            "roles": [
                {"id": "admin", "name": "Admin", "permissions": ["*"]},
                {"id": "manager", "name": "Manager", "permissions": ["products", "orders", "customers"]},
                {"id": "staff", "name": "Staff", "permissions": ["orders", "customers"]},
                {"id": "developer", "name": "Developer", "permissions": ["settings", "api"]},
            ]
        }
    
    async def create_role(
        self, 
        name: str, 
        permissions: list[str]
    ) -> dict:
        """Create custom role."""
        role_id = f"role_{uuid.uuid4().hex[:12]}"
        
        role = {
            "id": role_id,
            "name": name,
            "permissions": permissions,
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("roles", role)
        
        return role
    
    # ========== THEME & APPEARANCE ==========
    
    async def get_theme_settings(self) -> dict:
        """Get theme settings."""
        return {
            "theme": "default",
            "colors": {
                "primary": "#000000",
                "secondary": "#ffffff",
                "accent": "#ff0000",
            },
            "typography": {
                "heading_font": "Arial",
                "body_font": "Arial",
            },
            "layout": {
                "products_per_row": 4,
                "sidebar": True,
            },
        }
    
    async def update_theme_settings(
        self, 
        settings: dict
    ) -> dict:
        """Update theme settings."""
        if self.db:
            await self.db.create("theme_settings", settings)
        return {"updated": True}
    
    async def upload_theme_asset(
        self, 
        asset_data: dict
    ) -> dict:
        """Upload theme asset."""
        asset_id = f"asset_{uuid.uuid4().hex[:12]}"
        
        asset = {
            "id": asset_id,
            "filename": asset_data.get("filename"),
            "type": asset_data.get("type"),  # image, css, js
            "url": asset_data.get("url"),
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("theme_assets", asset)
        
        return asset
    
    # ========== PAGES & CONTENT ==========
    
    async def create_page(
        self, 
        page_data: dict
    ) -> dict:
        """Create page."""
        page_id = f"page_{uuid.uuid4().hex[:12]}"
        
        page = {
            "id": page_id,
            "title": page_data.get("title"),
            "slug": page_data.get("slug"),
            "content": page_data.get("content"),
            "template": page_data.get("template"),
            "status": page_data.get("status", "draft"),
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("pages", page)
        
        return page
    
    async def get_pages(self) -> dict:
        """Get all pages."""
        if self.db:
            result = await self.db.query("SELECT * FROM pages")
            return {"pages": result}
        return {"pages": []}
    
    # ========== SEO SETTINGS ==========
    
    async def get_seo_settings(self) -> dict:
        """Get SEO settings."""
        return {
            "meta_tags": {
                "home_title": "My Store",
                "home_description": "Welcome to my store",
            },
            "social_cards": {
                "image": None,
            },
            "url_structure": "/products/{title}",
        }
    
    async def update_seo_settings(
        self, 
        settings: dict
    ) -> dict:
        """Update SEO settings."""
        if self.db:
            await self.db.create("seo_settings", settings)
        return {"updated": True}
    
    # ========== EMAIL NOTIFICATIONS ==========
    
    async def get_email_settings(self) -> dict:
        """Get email settings."""
        return {
            "from_email": "noreply@store.com",
            "from_name": "My Store",
            "smtp": {
                "host": "smtp.example.com",
                "port": 587,
            },
        }
    
    async def update_email_settings(
        self, 
        settings: dict
    ) -> dict:
        """Update email settings."""
        if self.db:
            await self.db.create("email_settings", settings)
        return {"updated": True}
    
    async def get_notification_templates(
        self, 
        category: str | None = None
    ) -> dict:
        """Get email templates."""
        templates = [
            {"id": "order_confirmation", "name": "Order Confirmation", "trigger": "order_created"},
            {"id": "order_fulfilled", "name": "Order Shipped", "trigger": "order_fulfilled"},
            {"id": "password_reset", "name": "Password Reset", "trigger": "password_reset"},
        ]
        
        if category:
            templates = [t for t in templates if t.get("trigger") == category]
        
        return {"templates": templates}
    
    # ========== API KEYS ==========
    
    async def create_api_key(
        self, 
        name: str, 
        permissions: list[str]
    ) -> dict:
        """Create API key."""
        import secrets
        
        key_id = f"key_{uuid.uuid4().hex[:12]}"
        api_key = f"sk_{secrets.token_urlsafe(32)}"
        
        key_data = {
            "id": key_id,
            "api_key": api_key,
            "name": name,
            "permissions": permissions,
            "created_at": "NOW()",
            "last_used": None,
        }
        
        if self.db:
            await self.db.create("api_keys", key_data)
        
        return {"id": key_id, "api_key": api_key}
    
    async def revoke_api_key(
        self, 
        key_id: str
    ) -> dict:
        """Revoke API key."""
        if self.db:
            await self.db.merge(f"api_keys:{key_id}", {
                "revoked": True,
                "revoked_at": "NOW()",
            })
        return {"revoked": True}
    
    async def get_api_keys(self) -> dict:
        """Get API keys."""
        if self.db:
            result = await self.db.query("SELECT * FROM api_keys WHERE revoked != true")
            return {"keys": result}
        return {"keys": []}
    
    # ========== WEBHOOKS ==========
    
    async def create_webhook(
        self, 
        webhook_data: dict
    ) -> dict:
        """Create webhook."""
        webhook_id = f"webhook_{uuid.uuid4().hex[:12]}"
        
        webhook = {
            "id": webhook_id,
            "url": webhook_data.get("url"),
            "events": webhook_data.get("events"),  # order_created, product_created, etc.
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("webhooks", webhook)
        
        return webhook
    
    async def get_webhooks(self) -> dict:
        """Get webhooks."""
        if self.db:
            result = await self.db.query("SELECT * FROM webhooks")
            return {"webhooks": result}
        return {"webhooks": []}
    
    # ========== AUDIT LOG ==========
    
    async def create_audit_log(
        self, 
        action: str, 
        user_id: str | None,
        details: dict
    ) -> dict:
        """Create audit log entry."""
        log_id = f"log_{uuid.uuid4().hex[:12]}"
        
        log = {
            "id": log_id,
            "action": action,
            "user_id": user_id,
            "details": details,
            "ip_address": details.get("ip"),
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("audit_logs", log)
        
        return log
    
    async def get_audit_logs(
        self, 
        limit: int = 100,
        user_id: str | None = None
    ) -> dict:
        """Get audit logs."""
        query = "SELECT * FROM audit_logs"
        if user_id:
            query += f" WHERE user_id = '{user_id}'"
        query += f" ORDER BY created_at DESC LIMIT {limit}"
        
        if self.db:
            result = await self.db.query(query)
            return {"logs": result}
        return {"logs": []}
    
    # ========== BACKUPS ==========
    
    async def create_backup(
        self, 
        backup_type: str = "full"
    ) -> dict:
        """Create site backup."""
        backup_id = f"backup_{uuid.uuid4().hex[:12]}"
        
        backup = {
            "id": backup_id,
            "type": backup_type,  # full, partial
            "size": 0,  # calculated
            "status": "completed",
            "created_at": "NOW()",
        }
        
        if self.db:
            await self.db.create("backups", backup)
        
        return backup
    
    async def list_backups(self) -> dict:
        """List backups."""
        if self.db:
            result = await self.db.query("SELECT * FROM backups ORDER BY created_at DESC")
            return {"backups": result}
        return {"backups": []}
    
    # ========== AGENT CARD ==========
    
    def get_agent_card(self) -> dict:
        """Return AgentCard."""
        return {
            "name": "E-Commerce Site Admin",
            "description": "Site-wide administration and settings",
            "url": f"https://agents.example.com/{self.agent_id}",
            "version": "1.0.0",
            "skills": [
                # Site
                {"id": "site.info", "name": "get_site_info"},
                {"id": "site.settings", "name": "get_general_settings"},
                # Legal
                {"id": "legal.get", "name": "get_legal_settings"},
                # Shipping
                {"id": "shipping.zones", "name": "get_shipping_zones"},
                {"id": "shipping.create_zone", "name": "create_shipping_zone"},
                # Payment
                {"id": "payment.settings", "name": "get_payment_settings"},
                {"id": "payment.gateway", "name": "enable_gateway"},
                # Tax
                {"id": "tax.create", "name": "create_tax_rate"},
                # Users
                {"id": "user.create", "name": "create_user"},
                {"id": "user.list", "name": "get_users"},
                {"id": "user.deactivate", "name": "deactivate_user"},
                # Roles
                {"id": "role.list", "name": "get_roles"},
                {"id": "role.create", "name": "create_role"},
                # Theme
                {"id": "theme.get", "name": "get_theme_settings"},
                {"id": "theme.update", "name": "update_theme_settings"},
                # Pages
                {"id": "page.create", "name": "create_page"},
                {"id": "page.list", "name": "get_pages"},
                # SEO
                {"id": "seo.get", "name": "get_seo_settings"},
                {"id": "seo.update", "name": "update_seo_settings"},
                # Email
                {"id": "email.settings", "name": "get_email_settings"},
                {"id": "email.templates", "name": "get_notification_templates"},
                # API
                {"id": "api.key_create", "name": "create_api_key"},
                {"id": "api.key_list", "name": "get_api_keys"},
                {"id": "api.key_revoke", "name": "revoke_api_key"},
                # Webhooks
                {"id": "webhook.create", "name": "create_webhook"},
                {"id": "webhook.list", "name": "get_webhooks"},
                # Audit
                {"id": "audit.logs", "name": "get_audit_logs"},
                # Backups
                {"id": "backup.create", "name": "create_backup"},
                {"id": "backup.list", "name": "list_backups"},
            ],
        }


# ============================================================
# EXAMPLE USAGE
# ============================================================

async def main():
    # Create admin
    admin = SiteAdmin()
    
    # Get AgentCard
    card = admin.get_agent_card()
    print("Admin:", card["name"])
    print("Skills:", len(card["skills"]))
    
    # Site info
    info = await admin.get_site_info()
    print("Site:", info.get("name"))
    
    # Users
    users = await admin.get_users()
    print("Users:", len(users.get("users", [])))
    
    # Roles
    roles = await admin.get_roles()
    print("Roles:", len(roles.get("roles", [])))
    
    # API key
    api_key = await admin.create_api_key("Test Key", ["read_orders"])
    print("API Key:", api_key.get("api_key", "")[:20] + "...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())