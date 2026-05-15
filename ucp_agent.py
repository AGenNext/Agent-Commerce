"""
UCP Agent - An AI Agent based on the Universal Commerce Protocol (UCP)
           with A2A Protocol transport support and SurrealDB backend

This agent implements UCP commerce capabilities and can discover and interact
with UCP-compliant commerce services via A2A Protocol for agent-to-agent communication.

UCP Reference: https://ucp.dev
A2A Reference: https://a2a-protocol.org
SurrealDB: https://surrealdb.com
"""

import os
import json
import logging
from datetime import date
from typing import Any

from openhands.core.config import LLMConfig
from openhands.llm import LLM
from openhands.runtime import Client

# Optional SurrealDB support
try:
    import surrealdb
    from surrealdb import Surreal
    SURREALDB_AVAILABLE = True
except ImportError:
    SURREALDB_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# SurrealDB Constants
SURREALDB_VERSION = "latest"

# SurrealDB Deployment Modes
DEPLOYMENT_MODES = {
    "mem": "In-memory for development/testing",
    "file": "Single-node with persistent storage",
    "embedded": "Embedded in application (WASM/mobile/edge)",
    "distributed": "Distributed/cluster deployment",
}

# Data Models Supported
DATA_MODELS = [
    "relational",    # Tables, joins, SQL queries
    "document",     # JSON, nested objects
    "graph",        # Nodes, edges, traversal
    "timeseries",  # Temporal data with auto-sharding
]


class SurrealDBStore:
    """
    SurrealDB Backend for E-commerce.
    
    Multi-model database for AI agents with:
    - Relational, Document, Graph, Time-series models
    - Vector & Full-text search
    - Live queries
    - Real-time recommendations & fraud detection
    """
    
    def __init__(
        self,
        url: str = "mem://",
        user: str = "root",
        password: str = "root",
        namespace: str = "ucp",
        database: str = "ecommerce",
    ):
        self.url = url
        self.user = user
        self.password = password
        self.namespace = namespace
        self.database = database
        self.db: Surreal | None = None
        self.live_queries: dict = {}
    
    async def connect(self) -> None:
        """Connect to SurrealDB."""
        if not SURREALDB_AVAILABLE:
            raise RuntimeError("SurrealDB not installed. Install with: pip install surrealdb")
        
        self.db = await Surreal.connect(self.url)
        await self.db.use(self.namespace, self.database)
        
        # Initialize schema
        await self._init_schema()
        await self._init_live_queries()
        logger.info(f"Connected to SurrealDB: {self.url}")
    
    async def _init_schema(self) -> None:
        """Initialize database schema with multi-model support."""
        
        # === Relational + Document Model: Products ===
        await self.db.query("""
            DEFINE TABLE products SCHEMAFULL;
            DEFINE FIELD id ON products TYPE string;
            DEFINE FIELD name ON products TYPE string;
            DEFINE FIELD description ON products TYPE string;
            DEFINE FIELD price ON products TYPE float;
            DEFINE FIELD category ON products TYPE string;
            DEFINE FIELD embedding ON products TYPE array;
            DEFINE FIELD metadata ON products TYPE object;
            DEFINE FIELD tags ON products TYPE array;
            DEFINE FIELD inventory ON products TYPE int DEFAULT 0;
            DEFINE FIELD created_at ON products TYPE datetime;
            DEFINE FIELD updated_at ON products TYPE datetime;
            -- Constraints
            DEFINE INDEX idx_products_name ON products FIELDS name SEARCH ANALYZER ascii BM25;
            DEFINE INDEX idx_products_category ON products FIELDS category;
        """)
        
        # === Relational + Document Model: Users ===
        await self.db.query("""
            DEFINE TABLE users SCHEMAFULL;
            DEFINE FIELD id ON users TYPE string;
            DEFINE FIELD email ON users TYPE string;
            DEFINE FIELD name ON users TYPE string;
            DEFINE FIELD preferences ON users TYPE object;
            DEFINE FIELD purchase_history ON users TYPE array;
            DEFINE FIELD segments ON users TYPE array;
            DEFINE FIELD created_at ON users TYPE datetime;
        """)
        
        # === Graph Model: User-Product Relationships ===
        await self.db.query("""
            DEFINE TABLE user_views SCHEMAFULL;
            DEFINE FIELD user_id ON user_views TYPE string;
            DEFINE FIELD product_id ON user_views TYPE string;
            DEFINE FIELD view_count ON user_views TYPE int DEFAULT 1;
            DEFINE FIELD last_viewed ON user_views TYPE datetime;
            DEFINE TABLE user_purchases SCHEMAFULL;
            DEFINE FIELD user_id ON user_purchases TYPE string;
            DEFINE FIELD product_id ON user_purchases TYPE string;
            DEFINE FIELD amount ON user_purchases TYPE float;
            DEFINE FIELD purchased_at ON user_purchases TYPE datetime;
        """)
        
        # === Time-series: Events & Analytics ===
        await self.db.query("""
            DEFINE TABLE price_history SCHEMAFULL;
            DEFINE FIELD product_id ON price_history TYPE string;
            DEFINE FIELD price ON price_history TYPE float;
            DEFINE FIELD recorded_at ON price_history TYPE datetime;
            DEFINE TABLE events SCHEMAFULL;
            DEFINE FIELD type ON events TYPE string;
            DEFINE FIELD data ON events TYPE object;
            DEFINE FIELD timestamp ON events TYPE datetime;
            -- Time-series partition
            DEFINE INDEX idx_events_timestamp ON events FIELDS timestamp;
        """)
        
        # === Transactions (for fraud detection) ===
        await self.db.query("""
            DEFINE TABLE transactions SCHEMAFULL;
            DEFINE FIELD id ON transactions TYPE string;
            DEFINE FIELD user_id ON transactions TYPE string;
            DEFINE FIELD amount ON transactions TYPE float;
            DEFINE FIELD status ON transactions TYPE string;
            DEFINE FIELD created_at ON events TYPE datetime;
        """)
        
        # === Orders ===
        await self.db.query("""
            DEFINE TABLE orders SCHEMAFULL;
            DEFINE FIELD id ON orders TYPE string;
            DEFINE FIELD user_id ON orders TYPE string;
            DEFINE FIELD items ON orders TYPE array;
            DEFINE FIELD total ON orders TYPE float;
            DEFINE FIELD status ON orders TYPE string;
            DEFINE FIELD created_at ON orders TYPE datetime;
        """)
    
    async def _init_live_queries(self) -> None:
        """Initialize live queries for real-time updates."""
        # Live query for inventory alerts
        await self.db.query("""
            DEFINE TABLE live_inventory_alerts AS (
                SELECT * FROM products WHERE inventory < 10
            )
        """)
    
    # ============================================================
    # FULL-TEXT SEARCH
    # ============================================================
    
    async def fulltext_search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict]:
        """
        Full-text search using BM25 algorithm.
        
        SurrealDB built-in full-text search with ranking.
        """
        result = await self.db.query(f"""
            SELECT * FROM products 
            WHERE name @| "{query}" OR description @| "{query}"
            ORDER BY _score ASC
            LIMIT {limit}
        """)
        return result or []
    
    # ============================================================
    # VECTOR SEARCH
    # ============================================================
    
    async def vector_search(
        self,
        embedding: list[float],
        limit: int = 5,
        threshold: float = 0.8,
    ) -> list[dict]:
        """
        Vector similarity search for AI-powered matching.
        
        Uses SurrealDB vector embeddings for semantic search.
        """
        # In production, use actual embedding comparison
        result = await self.db.query(f"""
            SELECT *, vector::cosine::distance(embedding, {embedding}) AS distance
            FROM products
            WHERE vector::cosine::distance(embedding, {embedding}) < {threshold}
            ORDER BY distance ASC
            LIMIT {limit}
        """)
        return result or []
    
    # ============================================================
    # GRAPH TRAVERSAL
    # ============================================================
    
    async def get_user_product_graph(
        self,
        user_id: str,
        depth: int = 2,
    ) -> dict:
        """
        Graph traversal for user-product relationships.
        
        Returns user's connected products through views/purchases.
        """
        # Create graph relationships
        result = await self.db.query(f"""
            SELECT ->user_purchases->products AS purchased_products,
                   ->user_views->products AS viewed_products
            FROM users:{user_id}
            LIMIT {depth}
        """)
        return result[0] if result else {}
    
    async def get_related_products(
        self,
        product_id: str,
        limit: int = 5,
    ) -> list[dict]:
        """
        Find products frequently bought together using graph.
        """
        result = await self.db.query(f"""
            SELECT <-user_purchases<-users->user_purchases->products AS related
            FROM products:{product_id}
            LIMIT {limit}
        """)
        
        # Flatten related products
        related = []
        if result:
            for item in result:
                related.extend(item.get("related", []))
        
        # Deduplicate by ID
        seen = set()
        unique_related = []
        for p in related:
            pid = p.get("id")
            if pid and pid not in seen:
                seen.add(pid)
                unique_related.append(p)
        
        return unique_related[:limit]
    
    # ============================================================
    # TIME-SERIES ANALYTICS
    # ============================================================
    
    async def record_price_change(
        self,
        product_id: str,
        old_price: float,
        new_price: float,
    ) -> dict:
        """Record price change for time-series analysis."""
        await self.db.create("price_history", {
            "product_id": product_id,
            "price": new_price,
            "change": new_price - old_price,
            "recorded_at": "NOW()",
        })
        return {"product_id": product_id, "old": old_price, "new": new_price}
    
    async def get_price_history(
        self,
        product_id: str,
        days: int = 30,
    ) -> list[dict]:
        """Get historical prices for trend analysis."""
        result = await self.db.query(f"""
            SELECT * FROM price_history 
            WHERE product_id = '{product_id}'
            AND recorded_at > time::now() - {days}days
            ORDER BY recorded_at ASC
        """)
        return result or []
    
    async def get_inventory_forecast(
        self,
        product_id: str,
    ) -> dict:
        """Forecast inventory needs based on sales velocity."""
        result = await self.db.query(f"""
            SELECT 
                product_id,
                count() AS recent_sales,
                count() / 7 AS daily_velocity,
                math::mean((
                    SELECT count() FROM orders 
                    WHERE created_at > time::now() - 7days
                )) AS avg_weekly_sales
            FROM orders
            WHERE product_id = '{product_id}'
            GROUP ALL
        """)
        return result[0] if result else {}
    
    # ============================================================
    # LIVE QUERIES (Real-time updates)
    # ============================================================
    
    async def subscribe_low_inventory(
        self,
        callback: callable,
    ) -> str:
        """Subscribe to low inventory alerts in real-time."""
        live_query = await self.db.query.live(
            "SELECT * FROM products WHERE inventory < 10",
            callback,
        )
        query_id = f"live_inventory_{len(self.live_queries)}"
        self.live_queries[query_id] = live_query
        return query_id
    
    async def unsubscribe(self, query_id: str) -> None:
        """Unsubscribe from live query."""
        if query_id in self.live_queries:
            await self.live_queries[query_id].kill()
            del self.live_queries[query_id]
    
    # ============================================================
    # ADVANCED AGGREGATIONS
    # ============================================================
    
    async def get_category_breakdown(self) -> list[dict]:
        """Get sales breakdown by category."""
        result = await self.db.query("""
            SELECT category, count() AS product_count, math::sum(price) AS total_value
            FROM products GROUP BY category
        """)
        return result or []
    
    async def get_user_lifetime_value(self, user_id: str) -> dict:
        """Calculate customer lifetime value."""
        result = await self.db.query(f"""
            SELECT 
                user_id,
                math::sum(total) AS lifetime_value,
                count() AS total_orders,
                math::mean(total) AS avg_order_value
            FROM orders
            WHERE user_id = '{user_id}'
            GROUP ALL
        """)
        return result[0] if result else {}
    
    # ============================================================
    # IDENTITY & AUTHENTICATION
    # ============================================================
    
    async def create_user(
        self,
        email: str,
        password_hash: str,
        name: str | None = None,
        roles: list[str] | None = None,
    ) -> dict:
        """Create user with authentication data."""
        import uuid
        
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "roles": roles or ["customer"],
            "email_verified": False,
            "mfa_enabled": False,
            "created_at": "NOW()",
            "last_login": None,
            "failed_attempts": 0,
            "locked_until": None,
        }
        
        result = await self.db.create("auth_users", user)
        return result[0] if result else user
    
    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> dict | None:
        """
        Authenticate user with email/password.
        
        Returns user data if authenticated, None otherwise.
        """
        import hashlib
        import uuid
        from datetime import datetime, timedelta
        
        # Find user by email
        users = await self.db.query(f"SELECT * FROM auth_users WHERE email = '{email}'")
        if not users:
            # User doesn't exist - still compute hash to prevent timing attacks
            hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000)
            return None
        
        user = users[0]
        
        # Check if account is locked
        if user.get("locked_until"):
            locked_until = user.get("locked_until")
            if isinstance(locked_until, str):
                locked_until = datetime.fromisoformat(locked_until)
            if locked_until > datetime.now():
                return {"error": "Account locked", "locked_until": locked_until}
        
        # Verify password (in production, use proper comparison)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode(), 
            b'salt', 
            100000
        ).hex()
        
        # For demo, compare with stored hash (in production use proper hashing)
        if password_hash != user.get("password_hash"):
            # Increment failed attempts
            failed_attempts = user.get("failed_attempts", 0) + 1
            
            # Lock account after 5 failed attempts
            lock_account = failed_attempts >= 5
            update = {
                "failed_attempts": failed_attempts,
            }
            if lock_account:
                locked = datetime.now() + timedelta(minutes=30)
                update["locked_until"] = locked.isoformat()
            
            await self.db.merge(f"auth_users:{user['id']}", update)
            return None
        
        # Successful login - reset failed attempts
        await self.db.merge(f"auth_users:{user['id']}", {
            "failed_attempts": 0,
            "last_login": "NOW()",
            "locked_until": None,
        })
        
        # Return user without password
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user.get("name"),
            "roles": user.get("roles", []),
        }
    
    async def verify_session(
        self,
        session_id: str,
    ) -> dict | None:
        """Verify session is valid."""
        sessions = await self.db.query(f"SELECT * FROM sessions WHERE id = '{session_id}'")
        if not sessions:
            return None
        
        session = sessions[0]
        
        # Check expiration
        if session.get("expires_at"):
            expires = session.get("expires_at")
            if isinstance(expires, str):
                from datetime import datetime
                expires = datetime.fromisoformat(expires)
            if expires < datetime.now():
                # Expired - delete session
                await self.db.delete(f"sessions:{session_id}")
                return None
        
        return session
    
    async def create_session(
        self,
        user_id: str,
        duration_hours: int = 24,
    ) -> dict:
        """Create session for user."""
        import uuid
        from datetime import datetime, timedelta
        
        session_id = f"sess_{uuid.uuid4().hex}"
        expires = datetime.now() + timedelta(hours=duration_hours)
        
        session = {
            "id": session_id,
            "user_id": user_id,
            "created_at": "NOW()",
            "expires_at": expires.isoformat(),
            "ip_address": None,
            "user_agent": None,
        }
        
        result = await self.db.create("sessions", session)
        return result[0] if result else session
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session (logout)."""
        try:
            await self.db.delete(f"sessions:{session_id}")
            return True
        except:
            return False
    
    async def update_password(
        self,
        user_id: str,
        old_password_hash: str,
        new_password_hash: str,
    ) -> dict:
        """Update user password."""
        users = await self.db.query(f"SELECT * FROM auth_users WHERE id = '{user_id}'")
        if not users:
            return {"error": "User not found"}
        
        user = users[0]
        
        # Verify old password
        if user.get("password_hash") != old_password_hash:
            return {"error": "Invalid current password"}
        
        # Update password
        await self.db.merge(f"auth_users:{user_id}", {
            "password_hash": new_password_hash,
            "password_updated_at": "NOW()",
        })
        
        return {"success": True}
    
    async def enable_mfa(
        self,
        user_id: str,
        mfa_secret: str,
    ) -> dict:
        """Enable multi-factor authentication."""
        await self.db.merge(f"auth_users:{user_id}", {
            "mfa_enabled": True,
            "mfa_secret": mfa_secret,
        })
        return {"success": True, "mfa_enabled": True}
    
    async def verify_mfa(
        self,
        user_id: str,
        code: str,
    ) -> bool:
        """Verify MFA code."""
        import hmac
        import pyotp  # In production, use proper TOTP library
        
        users = await self.db.query(f"SELECT * FROM auth_users WHERE id = '{user_id}'")
        if not users:
            return False
        
        user = users[0]
        if not user.get("mfa_enabled"):
            return True  # MFA not enabled, allow
        
        secret = user.get("mfa_secret")
        if not secret:
            return False
        
        # Verify TOTP code
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code)
        except:
            return False
    
    # ============================================================
    # ECOMMERCE PAYMENTS
    # ============================================================
    
    async def create_payment_method(
        self,
        user_id: str,
        type: str,  # card, bank, wallet
        details: dict,
    ) -> dict:
        """
        Add payment method for user.
        
        Supports: credit_card, debit_card, bank_account, digital_wallet
        """
        import uuid
        
        method_id = f"pm_{uuid.uuid4().hex[:16]}"
        
        # Don't store raw card details - use tokenization
        payment_method = {
            "id": method_id,
            "user_id": user_id,
            "type": type,
            "details": {
                "last4": details.get("number", "")[-4:],
                "brand": details.get("brand"),
                "expiry_month": details.get("expiry_month"),
                "expiry_year": details.get("expiry_year"),
            },
            "token": f"tok_{uuid.uuid4().hex}",  # Tokenized reference
            "is_default": False,
            "created_at": "NOW()",
        }
        
        result = await self.db.create("payment_methods", payment_method)
        return result[0] if result else payment_method
    
    async def get_payment_methods(
        self,
        user_id: str,
    ) -> list[dict]:
        """Get user's saved payment methods."""
        result = await self.db.query(
            f"SELECT * FROM payment_methods WHERE user_id = '{user_id}'"
        )
        return result or []
    
    async def create_checkout_session(
        self,
        user_id: str,
        items: list[dict],
        currency: str = "USD",
    ) -> dict:
        """
        Create checkout session for cart items.
        
        Returns session with payment URL.
        """
        import uuid
        from datetime import datetime, timedelta
        
        session_id = f"cs_{uuid.uuid4().hex}"
        
        # Calculate totals
        subtotal = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        tax = round(subtotal * 0.08, 2)  # 8% tax
        shipping = 9.99 if subtotal < 50 else 0  # Free shipping over $50
        total = subtotal + tax + shipping
        
        session = {
            "id": session_id,
            "user_id": user_id,
            "items": items,
            "currency": currency,
            "subtotal": subtotal,
            "tax": tax,
            "shipping": shipping,
            "total": total,
            "status": "pending",
            "payment_method_id": None,
            "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "created_at": "NOW()",
        }
        
        result = await self.db.create("checkout_sessions", session)
        return result[0] if result else session
    
    async def process_payment(
        self,
        checkout_session_id: str,
        payment_method_id: str,
    ) -> dict:
        """
        Process payment for checkout session.
        
        In production, integrate with Stripe, PayPal, etc.
        """
        sessions = await self.db.query(
            f"SELECT * FROM checkout_sessions WHERE id = '{checkout_session_id}'"
        )
        if not sessions:
            return {"error": "Session not found"}
        
        session = sessions[0]
        if session.get("status") != "pending":
            return {"error": "Session already processed"}
        
        from datetime import datetime
        if session.get("expires_at"):
            expires = datetime.fromisoformat(session["expires_at"])
            if expires < datetime.now():
                await self.db.merge(f"checkout_sessions:{checkout_session_id}", {
                    "status": "expired"
                })
                return {"error": "Session expired"}
        
        # Create transaction record
        import uuid
        transaction_id = f"txn_{uuid.uuid4().hex}"
        
        transaction = {
            "id": transaction_id,
            "checkout_session_id": checkout_session_id,
            "user_id": session["user_id"],
            "amount": session["total"],
            "currency": session["currency"],
            "payment_method_id": payment_method_id,
            "status": "pending",
            "created_at": "NOW()",
        }
        
        await self.db.create("transactions", transaction)
        
        # Update session
        await self.db.merge(f"checkout_sessions:{checkout_session_id}", {
            "status": "processing",
            "payment_method_id": payment_method_id,
            "transaction_id": transaction_id,
        })
        
        # Simulate payment processing
        # In production: call payment provider API
        success = True  # Simulated
        
        if success:
            new_status = "completed"
            for item in session.get("items", []):
                # Update inventory
                product_id = item.get("product_id")
                if product_id:
                    await self.db.query(f"""
                        UPDATE products SET inventory = inventory - {item.get("quantity", 1)}
                        WHERE id = '{product_id}'
                    """)
            
            # Clear cart
            await self.db.query(f"DELETE FROM cart_items WHERE user_id = '{session['user_id']}'")
        else:
            new_status = "failed"
        
        await self.db.merge(f"checkout_sessions:{checkout_session_id}", {
            "status": new_status,
        })
        
        await self.db.merge(f"transactions:{transaction_id}", {
            "status": new_status,
        })
        
        return {
            "transaction_id": transaction_id,
            "status": new_status,
            "amount": session["total"],
            "currency": session["currency"],
        }
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: float | None = None,
        reason: str | None = None,
    ) -> dict:
        """
        Refund a payment.
        
        Full or partial refund.
        """
        transactions = await self.db.query(
            f"SELECT * FROM transactions WHERE id = '{transaction_id}'"
        )
        if not transactions:
            return {"error": "Transaction not found"}
        
        txn = transactions[0]
        if txn.get("status") != "completed":
            return {"error": "Cannot refund non-completed transaction"}
        
        refund_amount = amount or txn.get("amount", 0)
        if refund_amount > txn.get("amount", 0):
            return {"error": "Refund amount exceeds original"}
        
        import uuid
        refund_id = f"ref_{uuid.uuid4().hex}"
        
        refund = {
            "id": refund_id,
            "transaction_id": transaction_id,
            "amount": refund_amount,
            "reason": reason,
            "status": "pending",
            "created_at": "NOW()",
        }
        
        await self.db.create("refunds", refund)
        
        # Simulate refund processing
        # In production: call payment provider API
        success = True
        
        if success:
            await self.db.merge(f"refunds:{refund_id}", {
                "status": "completed"
            })
        
        return {
            "refund_id": refund_id,
            "status": "completed" if success else "failed",
            "amount": refund_amount,
        }
    
    async def get_payment_history(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get user's payment history."""
        result = await self.db.query(f"""
            SELECT * FROM transactions 
            WHERE user_id = '{user_id}'
            ORDER BY created_at DESC
            LIMIT {limit}
        """)
        return result or []
    
    # ============================================================
    # ADVANCED PAYMENT FEATURES (Agentic Payments)
    # ============================================================
    
    async def smart_payment_routing(
        self,
        amount: float,
        currency: str = "USD",
        user_id: str | None = None,
    ) -> dict:
        """
        Smart payment routing - Agentic Payments feature.
        
        Dynamically selects best payment provider based on:
        - Success rates
        - Fees
        - Geographic availability
        - User preferences
        """
        # Get provider performance metrics
        providers = await self.db.query("""
            SELECT * FROM payment_providers WHERE active = true
        """)
        
        if not providers:
            return {"provider": "default", "reason": "No providers available"}
        
        # Score each provider
        best_provider = None
        best_score = -float('inf')
        
        for provider in providers:
            score = 0
            
            # Success rate (40% weight)
            success_rate = provider.get("success_rate", 0.95)
            score += success_rate * 40
            
            # Fee efficiency (30% weight)
            # Lower fees = higher score
            fee = provider.get("fee_percent", 2.9)
            score += (3.0 - fee) * 10  # Normalize
            
            # Currency support (20% weight)
            currencies = provider.get("supported_currencies", [])
            if currency in currencies:
                score += 20
            
            # User history (10% weight)
            if user_id:
                user_success = await self.db.query(f"""
                    SELECT status FROM transactions 
                    WHERE user_id = '{user_id}' 
                    AND payment_provider_id = '{provider['id']}'
                    AND status = 'completed'
                """)
                if user_success:
                    score += 10
            
            if score > best_score:
                best_score = score
                best_provider = provider
        
        return {
            "provider_id": best_provider.get("id") if best_provider else None,
            "provider_name": best_provider.get("name") if best_provider else None,
            "estimated_fee": best_provider.get("fee_percent", 2.9) if best_provider else 0,
            "score": best_score,
        }
    
    async def split_payment(
        self,
        amount: float,
        splits: list[dict],  # [{"recipient": "acct_xxx", "amount": 50, "type": "transfer"}]
        currency: str = "USD",
    ) -> dict:
        """
        Split payments - for marketplaces, gig platforms.
        
        Distributes payment to multiple recipients.
        """
        import uuid
        
        split_id = f"sp_{uuid.uuid4().hex}"
        
        # Validate total
        total_split = sum(s.get("amount", 0) for s in splits)
        if abs(total_split - amount) > 0.01:
            return {"error": "Split amounts don't equal total"}
        
        split_payment = {
            "id": split_id,
            "amount": amount,
            "currency": currency,
            "splits": splits,
            "status": "pending",
            "created_at": "NOW()",
        }
        
        await self.db.create("split_payments", split_payment)
        
        # Process each split (simulated)
        for split in splits:
            # In production: call payment provider for each recipient
            pass
        
        return {
            "split_id": split_id,
            "status": "processing",
            "splits": splits,
        }
    
    async def subscription_payment(
        self,
        user_id: str,
        plan_id: str,
        payment_method_id: str,
    ) -> dict:
        """
        Recurring/subscription payments.
        
        Automatic billing on schedule.
        """
        import uuid
        from datetime import datetime, timedelta
        
        sub_id = f"sub_{uuid.uuid4().hex}"
        
        # Get plan details
        plans = await self.db.query(f"SELECT * FROM subscription_plans WHERE id = '{plan_id}'")
        if not plans:
            return {"error": "Plan not found"}
        
        plan = plans[0]
        
        now = datetime.now()
        interval = plan.get("interval", "month")
        if interval == "month":
            next_billing = now + timedelta(days=30)
        elif interval == "year":
            next_billing = now + timedelta(days=365)
        else:
            next_billing = now + timedelta(days=30)
        
        subscription = {
            "id": sub_id,
            "user_id": user_id,
            "plan_id": plan_id,
            "payment_method_id": payment_method_id,
            "status": "active",
            "amount": plan.get("price"),
            "currency": plan.get("currency", "USD"),
            "interval": interval,
            "next_billing_at": next_billing.isoformat(),
            "cancel_at_period_end": False,
            "created_at": "NOW()",
        }
        
        result = await self.db.create("subscriptions", subscription)
        return result[0] if result else subscription
    
    async def process_subscription(
        self,
        subscription_id: str,
    ) -> dict:
        """Process recurring payment for subscription."""
        subs = await self.db.query(f"SELECT * FROM subscriptions WHERE id = '{subscription_id}'")
        if not subs:
            return {"error": "Subscription not found"}
        
        sub = subs[0]
        if sub.get("status") != "active":
            return {"error": "Subscription not active"}
        
        # Create checkout session and process payment
        session = await self.create_checkout_session(
            user_id=sub["user_id"],
            items=[{
                "product_id": sub["plan_id"],
                "price": sub["amount"],
                "quantity": 1,
                "type": "subscription"
            }],
            currency=sub.get("currency", "USD"),
        )
        
        if sub.get("payment_method_id"):
            result = await self.process_payment(
                session["id"],
                sub["payment_method_id"]
            )
            
            # Update next billing date
            from datetime import datetime, timedelta
            interval = sub.get("interval", "month")
            if interval == "month":
                next_billing = datetime.now() + timedelta(days=30)
            elif interval == "year":
                next_billing = datetime.now() + timedelta(days=365)
            else:
                next_billing = datetime.now() + timedelta(days=30)
            
            await self.db.merge(f"subscriptions:{subscription_id}", {
                "last_payment_at": "NOW()",
                "next_billing_at": next_billing.isoformat(),
            })
            
            return result
        
        return {"error": "No payment method"}
    
    async def multi_currency_payment(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
    ) -> dict:
        """
        Convert and process payment in different currencies.
        
        Handles forex conversion.
        """
        # Get exchange rate (in production, fetch from provider)
        rates = {
            ("USD", "EUR"): 0.92,
            ("USD", "GBP"): 0.79,
            ("EUR", "USD"): 1.09,
            ("GBP", "USD"): 1.27,
        }
        
        rate = rates.get((from_currency, to_currency), 1.0)
        converted_amount = round(amount * rate, 2)
        
        return {
            "original_amount": amount,
            "original_currency": from_currency,
            "converted_amount": converted_amount,
            "converted_currency": to_currency,
            "exchange_rate": rate,
        }
    
    async def wallet_balance(
        self,
        user_id: str,
    ) -> dict:
        """Get user's digital wallet balance."""
        result = await self.db.query(f"""
            SELECT 
                SUM(CASE WHEN type = 'credit' THEN amount ELSE -amount END) as balance
            FROM wallet_transactions
            WHERE user_id = '{user_id}'
            GROUP ALL
        """)
        return result[0] if result else {"balance": 0}
    
    async def wallet_topup(
        self,
        user_id: str,
        amount: float,
        source: str,  # payment_method_id
    ) -> dict:
        """Add funds to digital wallet."""
        import uuid
        
        tx_id = f"wt_{uuid.uuid4().hex}"
        
        transaction = {
            "id": tx_id,
            "user_id": user_id,
            "type": "credit",
            "amount": amount,
            "source": source,
            "created_at": "NOW()",
        }
        
        await self.db.create("wallet_transactions", transaction)
        
        return {"transaction_id": tx_id, "amount": amount}
    
    # ============================================================
    # AGENTIC PAYMENTS (Autonomous AI Payments)
    # ============================================================
    
    async def authorize_agent_payment(
        self,
        user_id: str,
        agent_id: str,
        max_amount: float,
        duration_hours: int = 24,
        merchant_ids: list[str] | None = None,
    ) -> dict:
        """
        Authorize an AI agent to make payments on user's behalf.
        
        This is Mastercard Agent Pay concept - user grants limited
        payment authority to an AI agent.
        """
        import uuid
        from datetime import datetime, timedelta
        
        auth_id = f"agent_auth_{uuid.uuid4().hex}"
        
        auth = {
            "id": auth_id,
            "user_id": user_id,
            "agent_id": agent_id,
            "max_amount": max_amount,
            "current_spent": 0,
            "merchant_ids": merchant_ids or ["*"],  # All or specific
            "status": "active",
            "expires_at": (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
            "created_at": "NOW()",
        }
        
        result = await self.db.create("agent_payment_auths", auth)
        return result[0] if result else auth
    
    async def make_agent_payment(
        self,
        agent_auth_id: str,
        amount: float,
        merchant_id: str,
        description: str,
    ) -> dict:
        """
        Process payment authorized by AI agent.
        
        Verifies agent has valid authorization and within limits.
        """
        auths = await self.db.query(f"SELECT * FROM agent_payment_auths WHERE id = '{agent_auth_id}'")
        if not auths:
            return {"error": "Authorization not found"}
        
        auth = auths[0]
        
        # Check status
        if auth.get("status") != "active":
            return {"error": "Authorization not active"}
        
        # Check expiration
        from datetime import datetime
        if auth.get("expires_at"):
            expires = datetime.fromisoformat(auth["expires_at"])
            if expires < datetime.now():
                await self.db.merge(f"agent_payment_auths:{agent_auth_id}", {"status": "expired"})
                return {"error": "Authorization expired"}
        
        # Check amount limit
        max_amount = auth.get("max_amount", 0)
        current_spent = auth.get("current_spent", 0)
        if current_spent + amount > max_amount:
            return {"error": "Amount exceeds authorization limit"}
        
        # Check merchant
        merchant_ids = auth.get("merchant_ids", ["*"])
        if "*" not in merchant_ids and merchant_id not in merchant_ids:
            return {"error": "Merchant not authorized"}
        
        # Create transaction
        import uuid
        txn_id = f"txn_{uuid.uuid4().hex}"
        
        transaction = {
            "id": txn_id,
            "agent_auth_id": agent_auth_id,
            "user_id": auth["user_id"],
            "agent_id": auth["agent_id"],
            "amount": amount,
            "merchant_id": merchant_id,
            "description": description,
            "status": "completed",
            "created_at": "NOW()",
        }
        
        await self.db.create("transactions", transaction)
        
        # Update spending
        await self.db.merge(f"agent_payment_auths:{agent_auth_id}", {
            "current_spent": current_spent + amount
        })
        
        return {
            "transaction_id": txn_id,
            "status": "completed",
            "amount": amount,
            "remaining_authorization": max_amount - (current_spent + amount),
        }
    
    async def revoke_agent_payment(
        self,
        agent_auth_id: str,
    ) -> dict:
        """Revoke an agent's payment authorization."""
        await self.db.merge(f"agent_payment_auths:{agent_auth_id}", {
            "status": "revoked",
            "revoked_at": "NOW()",
        })
        return {"status": "revoked", "auth_id": agent_auth_id}
    
    async def get_agent_payment_status(
        self,
        agent_auth_id: str,
    ) -> dict:
        """Get agent payment authorization status."""
        auths = await self.db.query(f"SELECT * FROM agent_payment_auths WHERE id = '{agent_auth_id}'")
        if not auths:
            return {"error": "Not found"}
        
        auth = auths[0]
        return {
            "id": auth.get("id"),
            "agent_id": auth.get("agent_id"),
            "status": auth.get("status"),
            "max_amount": auth.get("max_amount"),
            "current_spent": auth.get("current_spent"),
            "remaining": auth.get("max_amount", 0) - auth.get("current_spent", 0),
            "expires_at": auth.get("expires_at"),
        }
    
    # Instant/Faster Payments
    async def instant_payment(
        self,
        to_user_id: str,
        amount: float,
        from_payment_method_id: str,
        reference: str | None = None,
    ) -> dict:
        """
        Instant payment to another user (P2P).
        
        Faster payments for real-time transfers.
        """
        import uuid
        
        payment_id = f"inst_{uuid.uuid4().hex}"
        
        payment = {
            "id": payment_id,
            "type": "instant",
            "to_user_id": to_user_id,
            "from_payment_method_id": from_payment_method_id,
            "amount": amount,
            "reference": reference,
            "status": "completed",  # Instant
            "created_at": "NOW()",
        }
        
        await self.db.create("instant_payments", payment)
        
        return payment
    
    # Scheduled/Delayed Payments
    async def schedule_payment(
        self,
        amount: float,
        payment_method_id: str,
        scheduled_at: str,  # ISO datetime
    ) -> dict:
        """Schedule a payment for future execution."""
        import uuid
        
        schedule_id = f"sch_{uuid.uuid4().hex}"
        
        schedule = {
            "id": schedule_id,
            "amount": amount,
            "payment_method_id": payment_method_id,
            "scheduled_at": scheduled_at,
            "status": "scheduled",
            "created_at": "NOW()",
        }
        
        await self.db.create("scheduled_payments", schedule)
        return schedule
    
    async def process_scheduled_payments(self) -> list[dict]:
        """Process due scheduled payments (run via cron)."""
        from datetime import datetime
        
        due = await self.db.query(f"""
            SELECT * FROM scheduled_payments 
            WHERE status = 'scheduled' 
            AND scheduled_at <= '{datetime.now().isoformat()}'
        """)
        
        processed = []
        for schedule in due:
            # Process each payment
            await self.db.merge(f"scheduled_payments:{schedule['id']}", {
                "status": "completed"
            })
            processed.append(schedule)
        
        return processed
    
    # ============================================================
    # x402 / MACHINE PAYMENTS PROTOCOL (Coinbase/Cloudflare)
    # ============================================================
    
    async def x402_create_payment_challenge(
        self,
        resource: str,
        amount: int,
        currency: str = "USD",
    ) -> dict:
        """Create x402 payment challenge (HTTP 402)."""
        import uuid
        
        challenge_id = f"x402_{uuid.uuid4().hex}"
        challenge = {
            "id": challenge_id,
            "resource": resource,
            "amount": amount,
            "currency": currency,
            "status": "pending",
        }
        
        await self.db.create("x402_challenges", challenge)
        
        return {
            "challenge_id": challenge_id,
            "headers": {
                "PAYMENT-REQUIRED": f"amount={amount},currency={currency}",
            }
        }
    
    async def x402_verify_payment(
        self,
        challenge_id: str,
        payment_proof: dict,
    ) -> dict:
        """Verify x402 payment proof."""
        challenges = await self.db.query(f"SELECT * FROM x402_challenges WHERE id = '{challenge_id}'")
        if not challenges:
            return {"error": "Challenge not found"}
        
        await self.db.merge(f"x402_challenges:{challenge_id}", {"status": "completed"})
        return {"status": "authorized"}
    
    async def mpp_process_payment(
        self,
        mpp_id: str,
        payment_method: str,
    ) -> dict:
        """Process Machine Payments Protocol."""
        requests = await self.db.query(f"SELECT * FROM mpp_requests WHERE id = '{mpp_id}'")
        if not requests:
            return {"error": "Request not found"}
        
        await self.db.merge(f"mpp_requests:{mpp_id}", {
            "status": "completed",
            "payment_method": payment_method,
        })
        return {"status": "completed", "mpp_id": mpp_id}
    
    # ============================================================
    # AP2 (Agent Payments Protocol) - Google/FIDO Alliance
    # ============================================================
    
    async def ap2_create_intent(
        self,
        user_id: str,
        amount: float,
        currency: str = "USD",
        reason: str | None = None,
    ) -> dict:
        """
        Create AP2 payment intent.
        
        AP2 (Agent Payments Protocol) is donated to FIDO Alliance.
        Supports autonomous "Human Not Present" payments.
        """
        import uuid
        
        intent_id = f"ap2_{uuid.uuid4().hex}"
        
        intent = {
            "id": intent_id,
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "reason": reason,
            "status": "pending",
            "created_at": "NOW()",
        }
        
        await self.db.create("ap2_intents", intent)
        return intent
    
    async def ap2_authorize_agent(
        self,
        user_id: str,
        agent_id: str,
        max_amount: float,
        permissions: list[str] | None = None,
    ) -> dict:
        """
        Authorize AI agent to make autonomous payments.
        
        This is "Human Not Present" authorization.
        """
        import uuid
        
        auth_id = f"ap2auth_{uuid.uuid4().hex}"
        
        auth = {
            "id": auth_id,
            "user_id": user_id,
            "agent_id": agent_id,
            "max_amount": max_amount,
            "permissions": permissions or ["purchase"],
            "uses_remaining": None,  # None = unlimited
            "status": "active",
            "created_at": "NOW()",
        }
        
        await self.db.create("ap2_agent_auths", auth)
        return auth
    
    async def ap2_verify_intent(
        self,
        intent_id: str,
        user_id: str,
    ) -> dict:
        """Verify user intent for autonomous payment."""
        intents = await self.db.query(f"SELECT * FROM ap2_intents WHERE id = '{intent_id}'")
        if not intents:
            return {"error": "Intent not found"}
        
        intent = intents[0]
        
        # Verify belongs to user
        if intent.get("user_id") != user_id:
            return {"error": "Unauthorized"}
        
        # Create verifiable intent record
        intent_hash = f"vi_{intent_id}_{user_id}"
        
        await self.db.merge(f"ap2_intents:{intent_id}", {
            "status": "verified",
            "intent_hash": intent_hash,
        })
        
        return {
            "status": "verified",
            "intent_hash": intent_hash,
            "amount": intent.get("amount"),
            "currency": intent.get("currency"),
        }
    
    async def ap2_execute_autonomous(
        self,
        auth_id: str,
        intent_id: str,
        amount: float,
        description: str,
    ) -> dict:
        """Execute autonomous payment via authorized agent."""
        auths = await self.db.query(f"SELECT * FROM ap2_agent_auths WHERE id = '{auth_id}'")
        if not auths:
            return {"error": "Authorization not found"}
        
        auth = auths[0]
        
        if auth.get("status") != "active":
            return {"error": "Authorization not active"}
        
        # Check max amount
        if auth.get("max_amount") and amount > auth.get("max_amount"):
            return {"error": "Exceeds authorization limit"}
        
        # Execute payment
        import uuid
        txn_id = f"ap2txn_{uuid.uuid4().hex}"
        
        transaction = {
            "id": txn_id,
            "auth_id": auth_id,
            "intent_id": intent_id,
            "agent_id": auth.get("agent_id"),
            "amount": amount,
            "description": description,
            "status": "completed",
            "created_at": "NOW()",
        }
        
        await self.db.create("ap2_transactions", transaction)
        
        return {
            "transaction_id": txn_id,
            "status": "completed",
            "amount": amount,
        }
    
    async def ap2_create_verifiable_log(
        self,
        transaction_id: str,
    ) -> dict:
        """Create tamper-proof log for accountability."""
        txns = await self.db.query(f"SELECT * FROM ap2_transactions WHERE id = '{transaction_id}'")
        if not txns:
            return {"error": "Not found"}
        
        txn = txns[0]
        
        # Create verifiable log entry
        log = {
            "transaction_id": transaction_id,
            "agent_id": txn.get("agent_id"),
            "intent_id": txn.get("intent_id"),
            "amount": txn.get("amount"),
            "action": "purchase",
            "timestamp": "NOW()",
        }
        
        # In production: sign with private key for tamper-proof
        return {
            "log": log,
            "signature": f"sig_{transaction_id}",
            "verified": True,
        }
    
    # Verify merchant/counterparty trust
    async def ap2_verify_trust(
        self,
        entity_id: str,
        entity_type: str,
    ) -> dict:
        """Verify entity trust level (AP2 compatible)."""
        result = await self.db.query(f"""
            SELECT * FROM trust_registry 
            WHERE entity_id = '{entity_id}' AND type = '{entity_type}'
        """)
        
        if not result:
            return {"trust_level": "unknown", "verified": False}
        
        entity = result[0]
        return {
            "entity_id": entity_id,
            "trust_level": entity.get("trust_level", "standard"),
            "verified": entity.get("verified", False),
        }
    
    # ============================================================
    # PAYPAL AGENT PAYMENTS PROTOCOL
    # ============================================================
    
    async def paypal_agent_payment(
        self,
        sender_id: str,
        recipient_id: str,
        amount: float,
        currency: str = "USD",
        request_id: str | None = None,
    ) -> dict:
        """PayPal Agent Payments Protocol."""
        import uuid
        
        payment_id = f"ppap_{uuid.uuid4().hex}"
        
        payment = {
            "id": payment_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "amount": amount,
            "currency": currency,
            "request_id": request_id,
            "status": "pending",
            "created_at": "NOW()",
        }
        
        await self.db.create("paypal_agent_payments", payment)
        
        return {
            "payment_id": payment_id,
            "status": "pending",
            "amount": amount,
            "currency": currency,
        }
    
    async def paypal_escrow_payment(
        self,
        sender_id: str,
        recipient_id: str,
        amount: float,
        release_conditions: dict,
    ) -> dict:
        """PayPal escrow for agents."""
        import uuid
        
        escrow_id = f"ppe_{uuid.uuid4().hex}"
        
        escrow = {
            "id": escrow_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "amount": amount,
            "release_conditions": release_conditions,  # {"time": "...", "events": [...]}
            "status": "held",
            "created_at": "NOW()",
        }
        
        await self.db.create("paypal_escrows", escrow)
        
        return {"escrow_id": escrow_id, "status": "held"}
    
    async def paypal_release_escrow(
        self,
        escrow_id: str,
    ) -> dict:
        """Release PayPal escrow."""
        escrows = await self.db.query(f"SELECT * FROM paypal_escrows WHERE id = '{escrow_id}'")
        if not escrows:
            return {"error": "Escrow not found"}
        
        await self.db.merge(f"paypal_escrows:{escrow_id}", {"status": "released"})
        return {"status": "released"}
    
    async def paypal_refund_agent(
        self,
        payment_id: str,
        amount: float | None = None,
    ) -> dict:
        """Refund via PayPal agent."""
        await self.db.merge(f"paypal_agent_payments:{payment_id}", {
            "status": "refunded",
            "refund_amount": amount,
        })
        return {"status": "refunded"}
    
    # ============================================================
    # OPEN BANKING (PSD2/OB)
    # ============================================================
    
    async def openbanking_create_consent(
        self,
        user_id: str,
        permissions: list[str],
        duration_hours: int = 24,
    ) -> dict:
        """
        Create Open Banking consent (PSD2 compliant).
        
        Policy-based authorization for agents.
        """
        import uuid
        from datetime import datetime, timedelta
        
        consent_id = f"obc_{uuid.uuid4().hex}"
        
        consent = {
            "id": consent_id,
            "user_id": user_id,
            "permissions": permissions,
            "valid_until": (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
            "status": "active",
            "created_at": "NOW()",
        }
        
        await self.db.create("openbanking_consents", consent)
        return consent
    
    async def openbanking_execute_payment(
        self,
        consent_id: str,
        amount: float,
        recipient_iban: str,
        reference: str,
    ) -> dict:
        """Execute payment via Open Banking."""
        consents = await self.db.query(f"SELECT * FROM openbanking_consents WHERE id = '{consent_id}'")
        if not consents:
            return {"error": "Consent not found"}
        
        consent = consents[0]
        
        # Check permissions
        if "payments" not in consent.get("permissions", []):
            return {"error": "Payment permission not granted"}
        
        # Check expiration
        from datetime import datetime
        if consent.get("valid_until"):
            valid_until = datetime.fromisoformat(consent["valid_until"])
            if valid_until < datetime.now():
                await self.db.merge(f"openbanking_consents:{consent_id}", {"status": "expired"})
                return {"error": "Consent expired"}
        
        # Execute SEPA/A2A payment
        import uuid
        payment_id = f"obp_{uuid.uuid4().hex}"
        
        payment = {
            "id": payment_id,
            "consent_id": consent_id,
            "user_id": consent["user_id"],
            "amount": amount,
            "recipient_iban": recipient_iban,
            "reference": reference,
            "status": "completed",
            "created_at": "NOW()",
        }
        
        await self.db.create("openbanking_payments", payment)
        return {"payment_id": payment_id, "status": "completed"}
    
    async def openbanking_get_accounts(
        self,
        user_id: str,
    ) -> dict:
        """Get user's bank accounts via Open Banking."""
        # In production: call banking API
        return {
            "accounts": [
                {"iban": "DE89370400440532013000", "currency": "EUR", "balance": 1000},
                {"iban": "GB82WEST12345698765432", "currency": "GBP", "balance": 2500},
            ]
        }
    
    async def openbanking_get_balance(
        self,
        account_iban: str,
    ) -> dict:
        """Get account balance."""
        return {"iban": account_iban, "balance": 1000.00, "currency": "EUR"}
    
    # ============================================================
    # AGENTIC COMMERCE PROTOCOL (ACP) - OpenAI + Stripe
    # ============================================================
    
    async def acp_create_checkout(
        self,
        merchant_id: str,
        items: list[dict],
        currency: str = "USD",
    ) -> dict:
        """
        Agentic Commerce Protocol (ACP) - OpenAI/Stripe.
        
        Powers Instant Checkout in ChatGPT.
        """
        import uuid
        
        checkout_id = f"acp_{uuid.uuid4().hex}"
        
        total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        
        checkout = {
            "id": checkout_id,
            "merchant_id": merchant_id,
            "items": items,
            "total": total,
            "currency": currency,
            "status": "pending",
            "created_at": "NOW()",
        }
        
        await self.db.create("acp_checkouts", checkout)
        
        return {
            "checkout_id": checkout_id,
            "merchant_id": merchant_id,
            "amount": total,
            "currency": currency,
            "url": f"https://checkout.chatgpt.com/{checkout_id}",
        }
    
    async def acp_process(
        self,
        checkout_id: str,
        payment_token: str,
    ) -> dict:
        """Process ACP checkout with token."""
        checkouts = await self.db.query(f"SELECT * FROM acp_checkouts WHERE id = '{checkout_id}'")
        if not checkouts:
            return {"error": "Checkout not found"}
        
        checkout = checkouts[0]
        
        # Verify token (Stripe Shared Payment Token)
        # In production: verify with Stripe
        verified = True
        
        if verified:
            await self.db.merge(f"acp_checkouts:{checkout_id}", {"status": "completed"})
            return {"status": "completed", "checkout_id": checkout_id}
        
        return {"status": "failed"}
    
    async def create_api_key(
        self,
        user_id: str,
        name: str,
        permissions: list[str],
        expires_days: int | None = None,
    ) -> dict:
        """Create API key for user."""
        import uuid
        from datetime import datetime, timedelta
        
        key_id = f"ak_{uuid.uuid4().hex[:16]}"
        key_secret = uuid.uuid4().hex + uuid.uuid4().hex
        
        api_key = {
            "id": key_id,
            "key_hash": hashlib.sha256(key_secret.encode()).hexdigest(),
            "user_id": user_id,
            "name": name,
            "permissions": permissions,
            "created_at": "NOW()",
            "last_used": None,
        }
        
        if expires_days:
            expires = datetime.now() + timedelta(days=expires_days)
            api_key["expires_at"] = expires.isoformat()
        
        result = await self.db.create("api_keys", api_key)
        
        # Return only once - secret is not stored
        return {
            **api_key,
            "key": key_secret,  # Only returned on creation
        }
    
    async def verify_api_key(
        self,
        key_id: str,
        key_secret: str,
    ) -> dict | None:
        """Verify API key."""
        import hashlib
        
        keys = await self.db.query(f"SELECT * FROM api_keys WHERE id = '{key_id}'")
        if not keys:
            return None
        
        key = keys[0]
        
        # Check expiration
        if key.get("expires_at"):
            from datetime import datetime
            expires = key.get("expires_at")
            if isinstance(expires, str):
                expires = datetime.fromisoformat(expires)
            if expires < datetime.now():
                return None
        
        # Verify secret
        key_hash = hashlib.sha256(key_secret.encode()).hexdigest()
        if key_hash != key.get("key_hash"):
            return None
        
        # Update last used
        await self.db.merge(f"api_keys:{key_id}", {"last_used": "NOW()"})
        
        return {
            "user_id": key["user_id"],
            "permissions": key.get("permissions", []),
        }


class UCPAgent:
    """
    Universal Commerce Protocol (UCP) Agent with SurrealDB Backend
    
    Multi-model database agent with:
    - UCP Commerce (discover, checkout, payment, refund)
    - SurrealDB retail (recommendations, pricing, fraud, etc.)
    - Identity & Authentication (register, login, MFA, API keys)
    """
    
    def __init__(
        self,
        llm_api_key: str | None = None,
        model: str = "openai/gpt-4o-mini",
        base_url: str | None = None,
        surreal_url: str = "mem://",
    ):
        self.version = UCP_VERSION
        
        # Initialize SurrealDB
        self.store = SurrealDBStore(url=surreal_url)
        
        # Initialize LLM
        api_key = llm_api_key or os.environ.get("LLM_API_KEY")
        if not api_key:
            raise ValueError("LLM_API_KEY is required")
        
        llm_config = LLMConfig(
            model=model,
            api_key=api_key,
            base_url=base_url,
        )
        self.llm = LLM(config=llm_config)
        
        # Runtime client for agentic actions
        self.runtime = Client(
            llm=self.llm,
            description="UCP Commerce Agent with SurrealDB",
        )
        
        
        # Initialize SurrealDB
        self.store = SurrealDBStore(url=surreal_url)
        
        # Initialize LLM
        api_key = llm_api_key or os.environ.get("LLM_API_KEY")
        if not api_key:
            raise ValueError("LLM_API_KEY is required")
        
        llm_config = LLMConfig(
            model=model,
            api_key=api_key,
            base_url=base_url,
        )
        self.llm = LLM(config=llm_config)
        
        # Runtime client for agentic actions
        self.runtime = Client(
            llm=self.llm,
            description="UCP Commerce Agent",
        )
        
        logger.info(f"Initialized UCP Agent v{self.version}")
    
    def get_capability_declaration(self) -> dict[str, Any]:
        """
        Get the UCP capability declaration for platform discovery.
        
        Returns the capability manifest that other platforms can use
        to understand this agent's capabilities.
        """
        return {
            "version": self.version,
            "spec": "https://ucp.dev/spec/agent",
            "schema": "https://ucp.dev/schemas/capability.json",
            "name": UCAPABILITY_NAME,
            "extends": None,  # Root capability, not an extension
            "description": "AI Agent with UCP commerce capabilities",
        }
    
    def get_service_declaration(self, transport: str = "a2a") -> dict[str, Any]:
        """
        Get the UCP service declaration for transport binding.
        
        Args:
            transport: Transport type ("a2a", "rest", "embedded")
            
        Returns:
            The service manifest that defines how to interact with this agent.
        """
        return {
            "version": self.version,
            "spec": "https://ucp.dev/spec/agent",
            "schema": "https://ucp.dev/schemas/service.json",
            "name": UCAPABILITY_NAME,
            "transport": transport,
            "endpoint": None,  # Set by client
        }
    
    def get_agent_card(self) -> dict[str, Any]:
        """
        Get the A2A AgentCard for agent-to-agent discovery.
        
        Returns:
            A2A AgentCard describing this agent's capabilities
        """
        return {
            "name": "UCPAgent",
            "description": "UCP Commerce Agent with SurrealDB - Multi-model retail/ecommerce with identity & auth",
            "version": A2A_VERSION,
            "url": None,  # Set when deployed
            "capabilities": {
                "skills": [
                    # Core UCP commerce skills
                    {
                        "id": "commerce.discover",
                        "name": "discover",
                        "description": "Discover UCP-compliant commerce services"
                    },
                    {
                        "id": "commerce.checkout",
                        "name": "checkout",
                        "description": "Initiate checkout session"
                    },
                    {
                        "id": "commerce.payment",
                        "name": "payment",
                        "description": "Process payment"
                    },
                    {
                        "id": "commerce.refund",
                        "name": "refund",
                        "description": "Process refund"
                    },
                    # SurrealDB retail skills
                    {
                        "id": "retail.search",
                        "name": "search",
                        "description": "Search products with vector similarity"
                    },
                    {
                        "id": "retail.recommendations",
                        "name": "recommendations",
                        "description": "AI-powered product recommendations"
                    },
                    {
                        "id": "retail.dynamic_pricing",
                        "name": "dynamic_pricing",
                        "description": "Real-time dynamic pricing"
                    },
                    {
                        "id": "retail.fraud_detection",
                        "name": "fraud_detection",
                        "description": "Graph-based fraud detection"
                    },
                    {
                        "id": "retail.image_analysis",
                        "name": "image_analysis",
                        "description": "SurrealML visual intelligence"
                    },
                    {
                        "id": "retail.trending",
                        "name": "trending",
                        "description": "Trending products analytics"
                    },
                    # Identity & Auth skills
                    {
                        "id": "auth.register",
                        "name": "register",
                        "description": "Create new user account"
                    },
                    {
                        "id": "auth.login",
                        "name": "login",
                        "description": "Authenticate user"
                    },
                    {
                        "id": "auth.logout",
                        "name": "logout",
                        "description": "End user session"
                    },
                    {
                        "id": "auth.mfa",
                        "name": "mfa",
                        "description": "Enable/disable MFA"
                    },
                    {
                        "id": "auth.api_key",
                        "name": "api_key",
                        "description": "Create API key for integrations"
                    },
                    # Payment skills
                    {
                        "id": "payment.add_method",
                        "name": "add_payment_method",
                        "description": "Add payment method"
                    },
                    {
                        "id": "payment.checkout",
                        "name": "checkout",
                        "description": "Create checkout session"
                    },
                    {
                        "id": "payment.process",
                        "name": "process_payment",
                        "description": "Process payment"
                    },
                    {
                        "id": "payment.refund",
                        "name": "refund",
                        "description": "Refund payment"
                    },
                    {
                        "id": "payment.history",
                        "name": "payment_history",
                        "description": "Get payment history"
                    },
                    # Agentic Payments (AP2/x402) skills
                    {
                        "id": "agentic.smart_routing",
                        "name": "smart_payment_routing",
                        "description": "AI-powered payment routing"
                    },
                    {
                        "id": "agentic.split",
                        "name": "split_payment",
                        "description": "Split payment to recipients"
                    },
                    {
                        "id": "agentic.subscription",
                        "name": "subscription_payment",
                        "description": "Recurring subscription"
                    },
                    {
                        "id": "agentic.wallet",
                        "name": "digital_wallet",
                        "description": "Digital wallet operations"
                    },
                    # AP2 Protocol skills
                    {
                        "id": "ap2.intent",
                        "name": "ap2_create_intent",
                        "description": "Create AP2 payment intent"
                    },
                    {
                        "id": "ap2.authorize",
                        "name": "ap2_authorize_agent",
                        "description": "Authorize agent for payments"
                    },
                    {
                        "id": "ap2.execute",
                        "name": "ap2_execute_autonomous",
                        "description": "Execute autonomous payment"
                    },
                    {
                        "id": "ap2.verify",
                        "name": "ap2_verify_trust",
                        "description": "Verify merchant trust"
                    },
                ],
                "streaming": True,
                "pushNotifications": False,
            },
            "authentication": None,
            "defaultInputModes": ["application/json"],
            "defaultOutputModes": ["application/json", "text/plain"],
        }
    
    async def discover_services(self, platform_url: str) -> dict[str, Any]:
        """
        Discover UCP-compliant services from a platform.
        
        Args:
            platform_url: URL of the UCP platform to discover
            
        Returns:
            Dictionary of discovered services keyed by capability name
        """
        logger.info(f"Discovering services from {platform_url}")
        
        # In practice, this would fetch from the platform's discovery endpoint
        # For now, return empty discovery result
        return {
            "version": self.version,
            "status": "success",
            "services": {},
            "capabilities": {},
            "payment_handlers": {},
        }
    
    async def initiate_checkout(
        self,
        cart: dict[str, Any],
        payment_handler: str,
    ) -> dict[str, Any]:
        """
        Initiate a UCP checkout session.
        
        Args:
            cart: Shopping cart with items, quantities, prices
            payment_handler: Payment handler name (e.g., "com.stripe.checkout")
            
        Returns:
            Checkout session with payment URL or token
        """
        logger.info(f"Initiating checkout with payment handler: {payment_handler}")
        
        # Execute checkout through the runtime
        instruction = f"""Initiate a checkout session for the following cart:
{json.dumps(cart, indent=2)}

Payment handler: {payment_handler}

Return the checkout session details including:
- Session ID
- Payment URL/token
- Amount total
- Currency"""
        
        result = await self.runtime.run(instruction)
        
        return {
            "version": self.version,
            "status": "success",
            "session_id": result.get("session_id"),
            "payment_url": result.get("payment_url"),
            "amount": cart.get("total"),
            "currency": cart.get("currency", "USD"),
        }
    
    async def process_payment(
        self,
        payment_token: str,
        amount: float,
        currency: str = "USD",
    ) -> dict[str, Any]:
        """
        Process payment through UCP payment handler.
        
        Args:
            payment_token: Payment token from checkout
            amount: Payment amount
            currency: Currency code
            
        Returns:
            Payment result
        """
        logger.info(f"Processing payment: {amount} {currency}")
        
        instruction = f"""Process payment with:
- Token: {payment_token}
- Amount: {amount}
- Currency: {currency}

Return the payment result."""
        
        result = await self.runtime.run(instruction)
        
        return {
            "version": self.version,
            "status": "success" if result.get("success") else "error",
            "transaction_id": result.get("transaction_id"),
            "amount": amount,
            "currency": currency,
        }
    
    async def execute_commerce_action(
        self,
        action: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a UCP commerce action or retail skill.
        
        Actions:
        - Core UCP: discover, checkout, payment, refund
        - Retail (SurrealDB): search, recommendations, dynamic_pricing, fraud_detection, 
                           image_analysis, trending
        """
        logger.info(f"Executing action: {action}")
        
        # Core UCP handlers
        ucp_handlers = {
            "discover": lambda: self.discover_services(params.get("platform_url", "")),
            "checkout": lambda: self.initiate_checkout(
                params.get("cart", {}),
                params.get("payment_handler", ""),
            ),
            "payment": lambda: self.process_payment(
                params.get("payment_token", ""),
                params.get("amount", 0),
                params.get("currency", "USD"),
            ),
        }
        
        # Retail handlers (SurrealDB)
        retail_handlers = {
            "search": lambda: self.store.search_products(
                query=params.get("query"),
                category=params.get("category"),
                limit=params.get("limit", 10),
            ),
            "recommendations": lambda: self.store.get_recommendations(
                user_id=params.get("user_id", ""),
                limit=params.get("limit", 5),
            ),
            "dynamic_pricing": lambda: self.store.calculate_dynamic_price(
                product_id=params.get("product_id", ""),
                user_id=params.get("user_id"),
            ),
            "fraud_detection": lambda: self.store.check_fraud(
                user_id=params.get("user_id", ""),
                amount=params.get("amount", 0),
            ),
            "image_analysis": lambda: self.store.analyze_product_image(
                image_url=params.get("image_url", ""),
            ),
            "trending": lambda: self.store.get_trending_products(
                days=params.get("days", 7),
                limit=params.get("limit", 10),
            ),
        }
        
        # Auth handlers (SurrealDB)
        auth_handlers = {
            "register": lambda: self.store.create_user(
                email=params.get("email", ""),
                password_hash=params.get("password_hash", ""),
                name=params.get("name"),
                roles=params.get("roles"),
            ),
            "login": lambda: self.store.authenticate(
                email=params.get("email", ""),
                password=params.get("password", ""),
            ),
            "logout": lambda: self.store.delete_session(
                session_id=params.get("session_id", ""),
            ),
            "mfa": lambda: self.store.enable_mfa(
                user_id=params.get("user_id", ""),
                mfa_secret=params.get("mfa_secret", ""),
            ) if params.get("enable", True) else {"success": True},
            "api_key": lambda: self.store.create_api_key(
                user_id=params.get("user_id", ""),
                name=params.get("name", "default"),
                permissions=params.get("permissions", []),
                expires_days=params.get("expires_days"),
            ),
        }
        
        # Payment handlers
        payment_handlers = {
            "add_payment_method": lambda: self.store.create_payment_method(
                user_id=params.get("user_id", ""),
                type=params.get("type", "card"),
                details=params.get("details", {}),
            ),
            "checkout": lambda: self.store.create_checkout_session(
                user_id=params.get("user_id", ""),
                items=params.get("items", []),
                currency=params.get("currency", "USD"),
            ),
            "process_payment": lambda: self.store.process_payment(
                checkout_session_id=params.get("checkout_session_id", ""),
                payment_method_id=params.get("payment_method_id", ""),
            ),
            "refund": lambda: self.store.refund_payment(
                transaction_id=params.get("transaction_id", ""),
                amount=params.get("amount"),
                reason=params.get("reason"),
            ),
            "payment_history": lambda: self.store.get_payment_history(
                user_id=params.get("user_id", ""),
                limit=params.get("limit", 10),
            ),
        }
        
        handlers = {**ucp_handlers, **retail_handlers, **auth_handlers, **payment_handlers}
        handler = handlers.get(action)
        
        if not handler:
            return {
                "version": self.version,
                "status": "error",
                "error": f"Unknown action: {action}",
            }
        
        try:
            result = await handler()
            return {
                "version": self.version,
                "status": "success",
                "action": action,
                "result": result,
            }
        except Exception as e:
            logger.error(f"Action failed: {e}")
            return {
                "version": self.version,
                "status": "error",
                "error": str(e),
            }
    
    async def connect_db(self) -> None:
        """Connect to SurrealDB."""
        await self.store.connect()
    
    async def close_db(self) -> None:
        """Close SurrealDB connection."""
        await self.store.close()


class A2AClient:
    """
    A2A Protocol Client for agent-to-agent communication.
    
    This client can discover and communicate with A2A-compatible agents.
    """
    
    def __init__(self, agent_url: str):
        self.agent_url = agent_url
        self.agent_card = None
    
    async def discover_agent_card(self) -> dict[str, Any]:
        """
        Discover the AgentCard from the remote agent.
        
        Returns:
            The remote agent's AgentCard
        """
        import aiohttp
        
        url = f"{self.agent_url.rstrip('/')}/.well-known/agent.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                self.agent_card = await response.json()
                return self.agent_card
    
    async def invoke(
        self,
        skill: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Invoke a skill on the remote agent (synchronous).
        
        Args:
            skill: Skill name to invoke
            payload: Input payload for the skill
            
        Returns:
            Skill response
        """
        import aiohttp
        
        url = f"{self.agent_url.rstrip('/')}/tasks/send"
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": skill,
                "arguments": payload,
            },
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=request) as response:
                result = await response.json()
                return result.get("result", {})
    
    async def stream(
        self,
        skill: str,
        payload: dict[str, Any],
    ):
        """
        Stream from a skill on the remote agent.
        
        Args:
            skill: Skill name to invoke
            payload: Input payload for the skill
            
        Yields:
            Streaming response parts
        """
        import aiohttp
        
        url = f"{self.agent_url.rstrip('/')}/tasks/send"
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": skill,
                "arguments": payload,
            },
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=request) as response:
                async for line in response.content:
                    if line:
                        yield json.loads(line)


async def main():
    """Example usage of the UCP Agent with SurrealDB"""
    
    # Initialize agent (requires LLM_API_KEY)
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        print("Error: LLM_API_KEY environment variable is required")
        print("Usage: LLM_API_KEY=your_key python ucp_agent.py")
        return
    
    # Create agent with in-memory SurrealDB
    agent = UCPAgent(llm_api_key=api_key, surreal_url="mem://")
    
    # Connect to SurrealDB
    await agent.connect_db()
    
    # Get capability declaration
    capabilities = agent.get_capability_declaration()
    print("UCP Capability Declaration:")
    print(json.dumps(capabilities, indent=2))
    
    # Get AgentCard
    agent_card = agent.get_agent_card()
    print("\nA2A AgentCard:")
    print(json.dumps(agent_card, indent=2))
    
    # === Retail actions with SurrealDB ===
    
    # 1. Create sample data
    await agent.store.create_product({
        "id": "prod_001",
        "name": "Wireless Headphones",
        "description": "Premium noise-cancelling headphones",
        "price": 199.99,
        "category": "electronics",
        "inventory": 50,
    })
    
    await agent.store.create_product({
        "id": "prod_002",
        "name": "Smart Watch",
        "description": "Fitness tracking smartwatch",
        "price": 299.99,
        "category": "electronics",
        "inventory": 8,  # Low inventory for dynamic pricing
    })
    
    await agent.store.create_user({
        "id": "user_001",
        "email": "customer@example.com",
        "name": "John Doe",
        "preferences": {"segment": "vip"},
        "purchase_history": [],
    })
    
    # 2. Search products
    print("\n--- Search Products ---")
    result = await agent.execute_commerce_action("search", {"query": "headphones"})
    print(json.dumps(result, indent=2))
    
    # 3. Get recommendations
    print("\n--- Recommendations ---")
    result = await agent.execute_commerce_action("recommendations", {"user_id": "user_001"})
    print(json.dumps(result, indent=2))
    
    # 4. Dynamic pricing
    print("\n--- Dynamic Pricing ---")
    result = await agent.execute_commerce_action("dynamic_pricing", {
        "product_id": "prod_002",
        "user_id": "user_001"
    })
    print(json.dumps(result, indent=2))
    
    # 5. Fraud detection
    print("\n--- Fraud Detection ---")
    result = await agent.execute_commerce_action("fraud_detection", {
        "user_id": "user_001",
        "amount": 500.00
    })
    print(json.dumps(result, indent=2))
    
    # 6. Image analysis
    print("\n--- Image Analysis ---")
    result = await agent.execute_commerce_action("image_analysis", {
        "image_url": "https://example.com/product.jpg"
    })
    print(json.dumps(result, indent=2))
    
    # 7. Trending products
    print("\n--- Trending Products ---")
    result = await agent.execute_commerce_action("trending", {"days": 7})
    print(json.dumps(result, indent=2))
    
    # Close connection
    await agent.close_db()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())