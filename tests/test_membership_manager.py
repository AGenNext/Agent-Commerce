import asyncio

from membership_manager import MembershipManager


def _run(coro):
    return asyncio.run(coro)


def test_agent_card_skills():
    mgr = MembershipManager()
    card = mgr.get_agent_card()
    assert card["name"] == "Digital Identity & Membership Manager"
    skill_ids = {s["id"] for s in card["skills"]}
    assert {"epin.redeem", "referral.commission", "referral.payout"} <= skill_ids


def test_create_profile_defaults_public():
    mgr = MembershipManager()
    profile = _run(mgr.create_profile({"handle": "ada", "display_name": "Ada"}))
    assert profile["handle"] == "ada"
    assert profile["is_public"] is True
    assert profile["id"].startswith("profile_")


def test_create_tier_defaults_currency_usd():
    mgr = MembershipManager()
    tier = _run(mgr.create_tier({"name": "Personal", "price": 99}))
    assert tier["priceCurrency"] == "USD"
    assert tier["epins_required"] == 1


def test_issue_epin_unused_with_code():
    mgr = MembershipManager()
    epin = _run(mgr.issue_epin("tier_123"))
    assert epin["status"] == "unused"
    assert len(epin["code"]) == 16  # 8 bytes hex, uppercased


def test_no_db_calls_are_safe():
    """Without a DB, fn-backed calls return a null result instead of raising."""
    mgr = MembershipManager()
    assert _run(mgr.redeem_epin("ABC", "user_1"))["membership"] is None
    assert _run(mgr.record_referral_commission("m_1"))["commission"] is None
    assert _run(mgr.create_referral_payout("user_1"))["batch"] is None
