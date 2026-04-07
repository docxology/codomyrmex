#!/usr/bin/env python3
"""
Authentication token management and validation utilities.

Usage:
    python auth_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
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
        return {"error": type(e).__name__}


_SAFE_JWT_CLAIM_KEYS = frozenset(
    {"exp", "iat", "nbf", "iss", "aud", "sub", "typ", "kid", "jti"}
)


def redact_jwt_payload_for_display(payload: dict) -> dict:
    """Return a copy safe to print (standard claims only; other values redacted)."""
    out: dict = {}
    for key, val in payload.items():
        if key in _SAFE_JWT_CLAIM_KEYS:
            out[key] = val
        elif isinstance(val, (int, float, bool)) or val is None:
            out[key] = val
        else:
            out[key] = "[redacted]"
    return out


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
    gen = subparsers.add_parser("generate", help="URL-safe random strings")
    gen.add_argument("--length", "-l", type=int, default=32)
    gen.add_argument("--prefix", "-p", default="")
    gen.add_argument("--count", "-n", type=int, default=1)

    # Decode JWT
    jwt_cmd = subparsers.add_parser("decode-jwt", help="Inspect JWT claims")
    jwt_cmd.add_argument("token", help="Encoded JWT (payload shown redacted)")

    # Hash password
    hash_cmd = subparsers.add_parser("hash", help="PBKDF2 digest of a passphrase")
    hash_cmd.add_argument("password", help="Passphrase to hash")
    hash_cmd.add_argument(
        "--show-digest",
        action="store_true",
        help="Print salt and digest hex (off by default).",
    )

    # Check env
    subparsers.add_parser("check-env", help="Check auth environment variables")

    args = parser.parse_args()

    if not args.command:
        print("🔐 Authentication Utilities\n")
        print("Commands:")
        print("  generate   - URL-safe random strings")
        print("  decode-jwt - Inspect JWT claims (values redacted)")
        print("  hash       - PBKDF2 digest of a passphrase")
        print("  check-env  - Check auth-related environment variables")
        return 0

    if args.command == "generate":
        print(f"🔑 Generating {args.count} value(s):\n")
        for _ in range(args.count):
            opaque = generate_token(args.length, args.prefix)
            print(f"   {opaque}")

    elif args.command == "decode-jwt":
        payload = decode_jwt_payload(args.token)
        print("📄 JWT Payload:\n")
        if "error" in payload:
            print(f"   ❌ {payload['error']}")
        else:
            print(json.dumps(redact_jwt_payload_for_display(payload), indent=2))
            if "exp" in payload:
                expiry = check_token_expiry(payload["exp"])
                if expiry["valid"]:
                    print(f"\n   ⏰ Expires in: {expiry['expires_in']}s")
                else:
                    print(f"\n   ❌ Expired {expiry['expired_ago']}s ago")

    elif args.command == "hash":
        salt, hashed = hash_password(args.password)
        print("🔒 Passphrase digest:\n")
        if args.show_digest:
            print(f"   Salt: {salt}")
            print(f"   Hash: {hashed}")
        else:
            print(
                "   Salt and hash generated (re-run with --show-digest to print hex values)."
            )

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
