"""OpenFGA authorization layer for Agent-Commerce.

Complements SurrealDB row-level PERMISSIONS with relationship-based (ReBAC)
authorization. See docs/authorization-openfga.md and authz/model.fga.
"""

from authz.fga_client import OpenFGAClient
from authz.sync import AuthzSync
from authz.tuples import EcosystemTuples, fga_obj, fga_user

__all__ = ["OpenFGAClient", "AuthzSync", "EcosystemTuples", "fga_obj", "fga_user"]
