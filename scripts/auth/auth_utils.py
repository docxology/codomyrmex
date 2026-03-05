#!/usr/bin/env python3
"""
Authentication token management and validation utilities.

Usage:
    python auth_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import base64
import hashlib
import json
import os
import secrets
import time


def generate_token(length: int = 32, prefix: str = "") -> str:
    """Generate a secure random token."""
    token = secrets.token_urlsafe(length)
    return f"{prefix}{token}" if prefix else token


def decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verification (for inspection only)."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {"error": "Invalid JWT format"}

        payload = parts[1]
        # Add padding
        payload += "=" * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        return {"error": str(e)}


def hash_password(password: str, salt: bytes | None = None) -> tuple:
    """Hash a password with salt."""
    if salt is None:
        salt = secrets.token_bytes(16)

    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex(), key.hex()


def check_token_expiry(exp: int) -> dict:
    """Check if a token expiry timestamp is valid."""
    now = int(time.time())
    if exp < now:
        return {"valid": False, "expired_ago": now - exp}
    return {"valid": True, "expires_in": exp - now}


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "auth"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/auth/config.yaml")

    parser = argparse.ArgumentParser(description="Authentication utilities")
    subparsers = parser.add_subparsers(dest="command")

    # Generate token
    gen = subparsers.add_parser("generate", help="Generate secure token")
    gen.add_argument("--length", "-l", type=int, default=32)
    gen.add_argument("--prefix", "-p", default="")
    gen.add_argument("--count", "-n", type=int, default=1)

    # Decode JWT
    jwt_cmd = subparsers.add_parser("decode-jwt", help="Decode JWT payload")
    jwt_cmd.add_argument("token", help="JWT token")

    # Hash password
    hash_cmd = subparsers.add_parser("hash", help="Hash a password")
    hash_cmd.add_argument("password", help="Password to hash")

    # Check env
    subparsers.add_parser("check-env", help="Check auth environment variables")

    args = parser.parse_args()

    if not args.command:
        print("🔐 Authentication Utilities\n")
        print("Commands:")
        print("  generate   - Generate secure tokens")
        print("  decode-jwt - Decode JWT payload (no verification)")
        print("  hash       - Hash a password with PBKDF2")
        print("  check-env  - Check auth environment variables")
        return 0

    if args.command == "generate":
        print(f"🔑 Generating {args.count} token(s):\n")
        for _ in range(args.count):
            token = generate_token(args.length, args.prefix)
            print(f"   {token}")

    elif args.command == "decode-jwt":
        payload = decode_jwt_payload(args.token)
        print("📄 JWT Payload:\n")
        if "error" in payload:
            print(f"   ❌ {payload['error']}")
        else:
            print(json.dumps(payload, indent=2))
            if "exp" in payload:
                expiry = check_token_expiry(payload["exp"])
                if expiry["valid"]:
                    print(f"\n   ⏰ Expires in: {expiry['expires_in']}s")
                else:
                    print(f"\n   ❌ Expired {expiry['expired_ago']}s ago")

    elif args.command == "hash":
        salt, hashed = hash_password(args.password)
        print("🔒 Password Hash:\n")
        print(f"   Salt: {salt}")
        print(f"   Hash: {hashed}")

    elif args.command == "check-env":
        auth_vars = [
            "API_KEY",
            "SECRET_KEY",
            "JWT_SECRET",
            "AUTH_TOKEN",
            "OAUTH_CLIENT_ID",
            "OAUTH_CLIENT_SECRET",
        ]
        print("🔍 Auth Environment Variables:\n")
        found = 0
        for var in auth_vars:
            value = os.environ.get(var)
            if value:
                masked = value[:4] + "..." if len(value) > 4 else "***"
                print(f"   ✅ {var}: {masked}")
                found += 1
            else:
                print(f"   ⚪ {var}: not set")
        print(f"\n   Found {found}/{len(auth_vars)} variables")

    return 0


if __name__ == "__main__":
    sys.exit(main())
