"""
Domain-event -> OpenFGA relationship-tuple mapping for the ecosystem.

Pure functions (no I/O) that translate an ecosystem event into the relationship
tuples defined in `authz/model.fga`. `AuthzSync` (authz/sync.py) feeds these to
the OpenFGA client. Keeping the mapping pure makes it unit-testable without a
server.

Id handling: accepts bare ids ("abc") or SurrealDB record ids ("users:abc") and
normalizes to FGA object strings ("user:abc").
"""

from __future__ import annotations


def _id(raw: str) -> str:
    """Return the id portion, dropping any SurrealDB 'table:' prefix."""
    return raw.split(":", 1)[1] if ":" in raw else raw


def fga_user(raw: str) -> str:
    return f"user:{_id(raw)}"


def fga_obj(fga_type: str, raw: str) -> str:
    return f"{fga_type}:{_id(raw)}"


class EcosystemTuples:
    """Builders returning lists of {user, relation, object} tuples."""

    @staticmethod
    def profile_created(
        profile_id: str,
        owner_id: str,
        tenant_id: str,
        org_id: str | None = None,
        is_public: bool = True,
    ) -> list[dict]:
        obj = fga_obj("identity_profile", profile_id)
        tuples = [
            {"user": fga_obj("tenant", tenant_id), "relation": "tenant", "object": obj},
            {"user": fga_user(owner_id), "relation": "owner", "object": obj},
        ]
        if is_public:
            tuples.append({"user": "user:*", "relation": "can_view", "object": obj})
        if org_id:
            tuples.append({"user": fga_obj("organization", org_id), "relation": "org", "object": obj})
        return tuples

    @staticmethod
    def program_created(program_id: str, tenant_id: str) -> list[dict]:
        return [{
            "user": fga_obj("tenant", tenant_id),
            "relation": "tenant",
            "object": fga_obj("membership_program", program_id),
        }]

    @staticmethod
    def tier_created(tier_id: str, program_id: str) -> list[dict]:
        return [{
            "user": fga_obj("membership_program", program_id),
            "relation": "program",
            "object": fga_obj("membership_tier", tier_id),
        }]

    @staticmethod
    def membership_created(membership_id: str, member_id: str, tier_id: str, tenant_id: str) -> list[dict]:
        obj = fga_obj("membership", membership_id)
        return [
            {"user": fga_obj("tenant", tenant_id), "relation": "tenant", "object": obj},
            {"user": fga_user(member_id), "relation": "member", "object": obj},
            {"user": fga_obj("membership_tier", tier_id), "relation": "tier", "object": obj},
        ]

    @staticmethod
    def epin_issued(epin_id: str, tenant_id: str, holder_id: str | None = None) -> list[dict]:
        obj = fga_obj("epin", epin_id)
        tuples = [{"user": fga_obj("tenant", tenant_id), "relation": "tenant", "object": obj}]
        if holder_id:
            tuples.append({"user": fga_user(holder_id), "relation": "holder", "object": obj})
        return tuples

    @staticmethod
    def referral_linked(sponsor_id: str, member_id: str, tenant_id: str) -> list[dict]:
        sponsor_node = fga_obj("network_node", sponsor_id)
        member_node = fga_obj("network_node", member_id)
        return [
            {"user": fga_obj("tenant", tenant_id), "relation": "tenant", "object": sponsor_node},
            {"user": fga_obj("tenant", tenant_id), "relation": "tenant", "object": member_node},
            {"user": fga_user(sponsor_id), "relation": "account", "object": sponsor_node},
            {"user": fga_user(member_id), "relation": "account", "object": member_node},
            # The downline node is the object; the sponsor node is the user, so
            # `upline` resolves transitively up the chain.
            {"user": sponsor_node, "relation": "sponsor", "object": member_node},
        ]

    @staticmethod
    def commission_created(commission_id: str, beneficiary_id: str, tenant_id: str) -> list[dict]:
        obj = fga_obj("referral_commission", commission_id)
        return [
            {"user": fga_obj("tenant", tenant_id), "relation": "tenant", "object": obj},
            {"user": fga_user(beneficiary_id), "relation": "beneficiary", "object": obj},
        ]

    @staticmethod
    def payout_created(
        batch_id: str,
        tenant_id: str,
        user_beneficiary_id: str | None = None,
        org_beneficiary_id: str | None = None,
    ) -> list[dict]:
        """Polymorphic beneficiary: a user (referral payout) or a merchant org's
        members (settlement payout), mirroring the generalized payout_batches."""
        obj = fga_obj("payout_batch", batch_id)
        tuples = [{"user": fga_obj("tenant", tenant_id), "relation": "tenant", "object": obj}]
        if user_beneficiary_id:
            tuples.append({"user": fga_user(user_beneficiary_id), "relation": "beneficiary", "object": obj})
        if org_beneficiary_id:
            tuples.append({
                "user": f"{fga_obj('organization', org_beneficiary_id)}#member",
                "relation": "beneficiary",
                "object": obj,
            })
        return tuples
