import asyncio

from authz.fga_client import OpenFGAClient
from authz.sync import AuthzSync
from authz.tuples import EcosystemTuples, fga_obj, fga_user


def _run(coro):
    return asyncio.run(coro)


# ---- id normalization ----

def test_id_normalization():
    assert fga_user("abc") == "user:abc"
    assert fga_user("users:abc") == "user:abc"       # strips SurrealDB table prefix
    assert fga_obj("membership", "memberships:m1") == "membership:m1"


# ---- tuple mapping ----

def test_profile_tuples_public_and_org():
    t = EcosystemTuples.profile_created("p1", "users:alice", "acme", org_id="store1", is_public=True)
    users = {(x["user"], x["relation"], x["object"]) for x in t}
    assert ("user:alice", "owner", "identity_profile:p1") in users
    assert ("user:*", "can_view", "identity_profile:p1") in users
    assert ("organization:store1", "org", "identity_profile:p1") in users


def test_profile_tuples_private_has_no_wildcard():
    t = EcosystemTuples.profile_created("p1", "alice", "acme", is_public=False)
    assert all(x["user"] != "user:*" for x in t)


def test_referral_tuples_build_sponsor_edge():
    t = EcosystemTuples.referral_linked("alice", "carol", "acme")
    edges = {(x["user"], x["relation"], x["object"]) for x in t}
    # downline node is the object; sponsor node is the user (transitive upline)
    assert ("network_node:alice", "sponsor", "network_node:carol") in edges
    assert ("user:alice", "account", "network_node:alice") in edges
    assert ("user:carol", "account", "network_node:carol") in edges


def test_payout_polymorphic_beneficiary():
    user_t = EcosystemTuples.payout_created("pb1", "acme", user_beneficiary_id="alice")
    assert any(x["user"] == "user:alice" and x["relation"] == "beneficiary" for x in user_t)

    org_t = EcosystemTuples.payout_created("pb2", "acme", org_beneficiary_id="store1")
    assert any(x["user"] == "organization:store1#member" for x in org_t)


# ---- client behavior without a server ----

def test_client_unconfigured_defaults_allow():
    client = OpenFGAClient(enabled=False, default_allow=True)
    assert client.configured is False
    assert _run(client.check("user:alice", "can_view", "identity_profile:p1")) is True


def test_client_unconfigured_can_fail_closed():
    client = OpenFGAClient(enabled=False, default_allow=False)
    assert _run(client.check("user:alice", "can_edit", "identity_profile:p1")) is False


def test_client_write_noop_when_unconfigured():
    client = OpenFGAClient(enabled=False)
    result = _run(client.write_tuples([{"user": "user:a", "relation": "owner", "object": "identity_profile:p1"}]))
    assert result["skipped"] is True


def test_sync_noop_when_unconfigured():
    sync = AuthzSync(OpenFGAClient(enabled=False))
    assert _run(sync.on_referral_linked("alice", "carol", "acme"))["skipped"] is True
    assert _run(sync.can("alice", "can_view", "identity_profile:p1")) is True
