"""
Digital Identity & Membership Manager Agent

Agent for the digital identity / commerce ecosystem layer: digital identity
profiles ("AI business cards"), membership programs and tiers, prepaid E-pin
activation, and the referral network with commission accounting.

Pairs with the SurrealQL schema in `surrealql/digital_identity_ecosystem.surql`
and reuses the shared payout pipeline in `surrealql/settlements_payouts.surql`.

Positioning: enabling Indian business to go global — open, digital-native
business transformation.

Manages:
- Digital identity profiles (handle, links, credentials, verification)
- Membership programs, tiers, and a member's active membership
- E-pin issuance and redemption
- Referral network (sponsor -> member) and referral commissions
"""

import secrets
import uuid


class MembershipManager:
    """
    Digital Identity & Membership Manager.

    Thin orchestration over SurrealDB, which owns schema, permissions, and the
    activation / referral functions (fn::redeem_epin,
    fn::record_referral_commission, fn::create_referral_payout_batch).
    """

    def __init__(self, db=None, config: dict | None = None):
        self.db = db
        self.config = config or {}
        self.agent_id = f"membership_mgr_{uuid.uuid4().hex[:8]}"

    # ========== IDENTITY PROFILES ==========

    async def create_profile(self, profile: dict) -> dict:
        """Create a digital identity profile ("AI business card")."""
        profile_id = f"profile_{uuid.uuid4().hex[:12]}"

        record = {
            "id": profile_id,
            "handle": profile.get("handle"),
            "display_name": profile.get("display_name"),
            "headline": profile.get("headline"),
            "links": profile.get("links", []),
            "is_public": profile.get("is_public", True),
            "tenant_id": profile.get("tenant_id", "default"),
            "created_at": "NOW()",
            **profile,
        }

        if self.db:
            await self.db.create("identity_profiles", record)

        return record

    async def get_profile(self, handle: str) -> dict:
        """Look up a public profile by its handle."""
        if self.db:
            result = await self.db.query(
                "SELECT * FROM identity_profiles WHERE handle = $handle LIMIT 1;",
                {"handle": handle},
            )
            return result[0] if result else {}
        return {}

    async def track_profile_event(
        self,
        profile_id: str,
        event_type: str = "view",  # view | link_tap | save_contact | share
        link_label: str | None = None,
    ) -> dict:
        """Record an engagement event against a profile."""
        if self.db:
            await self.db.create(
                "profile_views",
                {
                    "profile": profile_id,
                    "event_type": event_type,
                    "link_label": link_label,
                    "tenant_id": "default",
                    "created_at": "NOW()",
                },
            )
        return {"tracked": True, "event_type": event_type}

    # ========== MEMBERSHIP PROGRAMS & TIERS ==========

    async def create_program(self, name: str, description: str | None = None) -> dict:
        """Create a membership program."""
        program = {
            "id": f"program_{uuid.uuid4().hex[:12]}",
            "name": name,
            "description": description,
            "tenant_id": "default",
            "created_at": "NOW()",
        }
        if self.db:
            await self.db.create("membership_programs", program)
        return program

    async def create_tier(self, tier: dict) -> dict:
        """Create a membership tier (plan)."""
        record = {
            "id": f"tier_{uuid.uuid4().hex[:12]}",
            "name": tier.get("name"),
            "price": tier.get("price", 0),
            "priceCurrency": tier.get("priceCurrency", "USD"),
            "epins_required": tier.get("epins_required", 1),
            "referral_rate": tier.get("referral_rate", 0),
            "benefits": tier.get("benefits", []),
            "tenant_id": tier.get("tenant_id", "default"),
            "created_at": "NOW()",
            **tier,
        }
        if self.db:
            await self.db.create("membership_tiers", record)
        return record

    async def list_tiers(self) -> dict:
        """List active membership tiers."""
        if self.db:
            result = await self.db.query(
                "SELECT * FROM membership_tiers WHERE is_active = true ORDER BY price;"
            )
            return {"tiers": result}
        return {"tiers": []}

    # ========== E-PINS ==========

    async def issue_epin(self, tier_id: str, issued_to: str | None = None) -> dict:
        """Issue a prepaid single-use activation E-pin for a tier."""
        epin = {
            "code": secrets.token_hex(8).upper(),
            "tier": tier_id,
            "status": "unused",
            "issued_to": issued_to,
            "tenant_id": "default",
            "created_at": "NOW()",
        }
        if self.db:
            await self.db.create("epins", epin)
        return {"code": epin["code"], "status": "unused"}

    async def redeem_epin(self, code: str, member_id: str) -> dict:
        """Redeem an E-pin to activate a membership (SurrealDB fn::redeem_epin)."""
        if self.db:
            result = await self.db.query(
                "RETURN fn::redeem_epin($code, type::thing('users', $member));",
                {"code": code, "member": member_id},
            )
            return {"membership": result}
        return {"membership": None, "code": code, "member": member_id}

    # ========== REFERRAL NETWORK ==========

    async def link_referral(
        self,
        sponsor_id: str,
        member_id: str,
        code: str | None = None,
    ) -> dict:
        """Record a sponsor -> member referral edge (depth 1)."""
        if self.db:
            await self.db.query(
                "RELATE type::thing('users', $sponsor)->referred->type::thing('users', $member) "
                "CONTENT { tenant_id: 'default', code: $code, depth: 1 };",
                {"sponsor": sponsor_id, "member": member_id, "code": code},
            )
        return {"linked": True, "sponsor": sponsor_id, "member": member_id}

    async def record_referral_commission(self, membership_id: str) -> dict:
        """Credit the direct sponsor for a new membership (fn::record_referral_commission)."""
        if self.db:
            result = await self.db.query(
                "RETURN fn::record_referral_commission(type::thing('memberships', $m));",
                {"m": membership_id},
            )
            return {"commission": result}
        return {"commission": None}

    async def list_commissions(self, beneficiary_id: str, status: str | None = None) -> dict:
        """List a referrer's commissions."""
        if self.db:
            query = "SELECT * FROM referral_commissions WHERE beneficiary = type::thing('users', $b)"
            params = {"b": beneficiary_id}
            if status:
                query += " AND status = $status"
                params["status"] = status
            query += " ORDER BY created_at DESC;"
            result = await self.db.query(query, params)
            return {"commissions": result}
        return {"commissions": []}

    async def create_referral_payout(self, beneficiary_id: str, currency: str = "USD") -> dict:
        """Batch a referrer's pending commissions into the shared payout pipeline."""
        if self.db:
            result = await self.db.query(
                "RETURN fn::create_referral_payout_batch(type::thing('users', $b), $currency);",
                {"b": beneficiary_id, "currency": currency},
            )
            return {"batch": result}
        return {"batch": None}

    # ========== AGENT CARD ==========

    def get_agent_card(self) -> dict:
        """Return AgentCard."""
        return {
            "name": "Digital Identity & Membership Manager",
            "description": "Digital identity profiles, memberships, E-pins, and referrals",
            "url": f"https://agents.example.com/{self.agent_id}",
            "version": "1.0.0",
            "skills": [
                {"id": "profile.create", "name": "create_profile"},
                {"id": "profile.get", "name": "get_profile"},
                {"id": "profile.track", "name": "track_profile_event"},
                {"id": "program.create", "name": "create_program"},
                {"id": "tier.create", "name": "create_tier"},
                {"id": "tier.list", "name": "list_tiers"},
                {"id": "epin.issue", "name": "issue_epin"},
                {"id": "epin.redeem", "name": "redeem_epin"},
                {"id": "referral.link", "name": "link_referral"},
                {"id": "referral.commission", "name": "record_referral_commission"},
                {"id": "referral.commissions", "name": "list_commissions"},
                {"id": "referral.payout", "name": "create_referral_payout"},
            ],
        }


# ============================================================
# EXAMPLE
# ============================================================

async def main():
    manager = MembershipManager()

    print("Agent:", manager.get_agent_card()["name"])
    print("Skills:", len(manager.get_agent_card()["skills"]))

    # Identity profile
    profile = await manager.create_profile({
        "handle": "ada",
        "display_name": "Ada Lovelace",
        "headline": "Founder, Analytical Engines",
        "links": [{"label": "Site", "url": "https://example.com", "kind": "website"}],
    })
    print("Profile:", profile["id"])

    # Membership tier
    tier = await manager.create_tier({
        "name": "Personal",
        "price": 99,
        "priceCurrency": "INR",
        "epins_required": 1,
        "referral_rate": 0.2,
    })
    print("Tier:", tier["id"])

    # E-pin
    epin = await manager.issue_epin(tier["id"])
    print("E-pin:", epin["code"])


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
