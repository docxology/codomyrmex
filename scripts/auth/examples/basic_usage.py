#!/usr/bin/env python3
"""
Authentication & Authorization - Real Usage Examples

Demonstrates actual auth capabilities:
- Token management
- Authenticator usage
- API Key management
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.auth import (
    Authenticator
)

def main():
    setup_logging()
    print_info("Running Auth Examples...")

    # 2. API Key Manager & Authenticator Flow
    print_info("Testing integrated Auth flow (Key -> Token -> Auth)...")
    try:
        auth = Authenticator()
        akm = auth.api_key_manager
        
        # 1. Generate key
        key = akm.generate_api_key(user_id="dev_user", permissions=["read", "data_access"])
        print_success(f"  Generated API Key: {key[:15]}...")
        
        # 2. Authenticate with key
        token = auth.authenticate(credentials={"api_key": key})
        if token:
            print_success(f"  Authenticated successfully. Session Token: {token.token_id[:10]}...")
            
            # 3. Check Authorization
            if auth.authorize(token, resource="database", permission="data_access"):
                print_success("  Authorization check passed for 'data_access'.")
            else:
                print_error("  Authorization check failed unexpectedly.")
    except Exception as e:
        print_error(f"  Auth flow failed: {e}")

    # 3. Token Management directly
    print_info("Testing TokenManager directly...")
    try:
        tm = auth.token_manager
        token = tm.create_token(user_id="user456", permissions=["read"])
        if tm.validate_token(token):
            print_success("  Direct Token validation functional.")
    except Exception as e:
        print_error(f"  Direct TokenManager test failed: {e}")

    print_success("Auth examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
