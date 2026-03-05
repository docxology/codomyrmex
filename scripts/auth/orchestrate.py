#!/usr/bin/env python3
"""
Orchestrator for auth module.

This script demonstrates and verifies the full lifecycle of the auth module:
1. Role-Based Access Control (RBAC) Setup (registering roles, inheritance)
2. User Registration (creating users, assigning roles)
3. Authentication (password-based login, API key generation)
4. Authorization (checking permissions using signed tokens and API keys)
5. Lifecycle Management (token refresh, token revocation, API key rotation)
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.auth import Authenticator
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_section,
    print_success,
    setup_logging,
)


def run_auth_lifecycle():
    setup_logging()
    print_section("Auth Module Comprehensive Lifecycle Demonstration")

    # 1. Initialize Authenticator (Singleton)
    auth = Authenticator()
    print_info("Authenticator singleton initialized.")

    # 2. RBAC Setup
    print_section("1. RBAC Setup")
    auth.permissions.register_role("reader", ["data.read", "reports.list"])
    auth.permissions.register_role("editor", ["data.write", "reports.create"])
    auth.permissions.add_inheritance("editor", "reader")
    auth.permissions.register_role("admin", ["*"])
    print_success("  Registered roles: reader, editor (inherits reader), and admin (*).")

    # 3. User Registration
    print_section("2. User Registration")
    auth.register_user("alice", "alice_pass", roles=["editor"])
    auth.register_user("bob", "bob_pass", roles=["reader"])
    auth.register_user("charlie", "charlie_pass", roles=["admin"])
    print_success("  Registered users: alice (editor), bob (reader), charlie (admin).")

    # 4. Authentication (Password)
    print_section("3. Password Authentication")
    alice_token = auth.authenticate({"username": "alice", "password": "alice_pass"})
    if alice_token and alice_token.jwt:
        print_success(f"  Alice authenticated. Token: {alice_token.token_id[:10]}...")
        print_info(f"  Signed JWT length: {len(alice_token.jwt)}")
    else:
        print_error("  Alice authentication failed.")
        return 1

    # 5. Authorization
    print_section("4. Authorization Enforcement")
    # Alice (editor) should have data.read (inherited) and data.write (direct)
    if auth.authorize(alice_token, "database", "data.read"):
        print_success("  Alice authorized for 'data.read' (Inherited).")
    else:
        print_error("  Alice NOT authorized for 'data.read'.")
        return 1

    if auth.authorize(alice_token, "database", "data.write"):
        print_success("  Alice authorized for 'data.write' (Direct).")
    else:
        print_error("  Alice NOT authorized for 'data.write'.")
        return 1

    # Bob (reader) should NOT have data.write
    bob_token = auth.authenticate({"username": "bob", "password": "bob_pass"})
    if auth.authorize(bob_token, "database", "data.write"):
        print_error("  Bob authorized for 'data.write' unexpectedly.")
        return 1
    else:
        print_success("  Bob denied access to 'data.write' (Correct).")

    # 6. API Key Management
    print_section("5. API Key Management")
    alice_api_key = auth.api_key_manager.generate("alice", permissions=["data.read", "api.access"])
    print_success(f"  Generated API Key for Alice: {alice_api_key[:15]}...")

    # Authenticate via API key
    key_token = auth.authenticate({"api_key": alice_api_key})
    if key_token and auth.authorize(key_token, "api", "api.access"):
        print_success("  Authenticated and authorized via Alice's API key.")
    else:
        print_error("  API key authentication or authorization failed.")
        return 1

    # API Key Rotation
    new_api_key = auth.api_key_manager.rotate(alice_api_key)
    if new_api_key and not auth.api_key_manager.validate(alice_api_key):
        print_success(f"  Alice's API key rotated. New key: {new_api_key[:15]}...")
    else:
        print_error("  API key rotation failed.")
        return 1

    # 7. Token Lifecycle (Revocation)
    print_section("6. Token Lifecycle Management")
    auth.revoke_token(alice_token)
    if not auth.authorize(alice_token, "database", "data.read"):
        print_success("  Alice's session token revoked and authorization failed (Correct).")
    else:
        print_error("  Alice's token still active after revocation.")
        return 1

    # 8. Token Lifecycle (Refresh)
    new_bob_token = auth.refresh_token(bob_token)
    if new_bob_token and new_bob_token.token_id != bob_token.token_id:
        print_success(f"  Bob's token refreshed. New ID: {new_bob_token.token_id[:10]}...")
    else:
        print_error("  Bob's token refresh failed.")
        return 1

    print_section("Auth Lifecycle Demonstration Completed Successfully")
    return 0

if __name__ == "__main__":
    sys.exit(run_auth_lifecycle())
