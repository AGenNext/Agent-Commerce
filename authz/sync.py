"""
Authorization sync: write ecosystem relationship tuples into OpenFGA.

Bridges the domain managers (e.g. MembershipManager) and the OpenFGA client.
Each `on_*` method maps an event to tuples via EcosystemTuples and writes them.
All methods are safe no-ops when the client is unconfigured, so the app runs
with or without an OpenFGA server.
"""

from __future__ import annotations

from authz.fga_client import OpenFGAClient
from authz.tuples import EcosystemTuples


class AuthzSync:
    """Writes relationship tuples for ecosystem events, and answers checks."""

    def __init__(self, client: OpenFGAClient | None = None):
        self.client = client or OpenFGAClient.from_env()
        self.tuples = EcosystemTuples()

    # ---- checks ----

    async def can(self, user_id: str, relation: str, fga_object: str) -> bool:
        """check(user, relation, object). `user_id` is normalized to user:<id>."""
        from authz.tuples import fga_user
        return await self.client.check(fga_user(user_id), relation, fga_object)

    # ---- event -> tuple writes ----

    async def on_profile_created(self, profile_id, owner_id, tenant_id, org_id=None, is_public=True) -> dict:
        return await self.client.write_tuples(
            self.tuples.profile_created(profile_id, owner_id, tenant_id, org_id, is_public)
        )

    async def on_program_created(self, program_id, tenant_id) -> dict:
        return await self.client.write_tuples(self.tuples.program_created(program_id, tenant_id))

    async def on_tier_created(self, tier_id, program_id) -> dict:
        return await self.client.write_tuples(self.tuples.tier_created(tier_id, program_id))

    async def on_membership_created(self, membership_id, member_id, tier_id, tenant_id) -> dict:
        return await self.client.write_tuples(
            self.tuples.membership_created(membership_id, member_id, tier_id, tenant_id)
        )

    async def on_epin_issued(self, epin_id, tenant_id, holder_id=None) -> dict:
        return await self.client.write_tuples(self.tuples.epin_issued(epin_id, tenant_id, holder_id))

    async def on_referral_linked(self, sponsor_id, member_id, tenant_id) -> dict:
        return await self.client.write_tuples(
            self.tuples.referral_linked(sponsor_id, member_id, tenant_id)
        )

    async def on_commission_created(self, commission_id, beneficiary_id, tenant_id) -> dict:
        return await self.client.write_tuples(
            self.tuples.commission_created(commission_id, beneficiary_id, tenant_id)
        )

    async def on_payout_created(self, batch_id, tenant_id, user_beneficiary_id=None, org_beneficiary_id=None) -> dict:
        return await self.client.write_tuples(
            self.tuples.payout_created(batch_id, tenant_id, user_beneficiary_id, org_beneficiary_id)
        )
