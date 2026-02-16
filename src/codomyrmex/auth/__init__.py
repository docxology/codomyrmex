"""
Authentication module for Codomyrmex.

This module provides authentication and authorization with API key management,
OAuth integration, and access control.
"""

from typing import Optional

from codomyrmex.exceptions import CodomyrmexError

from .core import Authenticator
from .providers import APIKeyManager
from .rbac import PermissionRegistry
from .tokens import Token, TokenManager, TokenValidator

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the auth module."""
    return {
        "providers": {
            "help": "List available authentication providers",
            "handler": lambda **kwargs: print(
                "Auth Providers:\n"
                f"  - Authenticator: {Authenticator.__name__}\n"
                f"  - API Key Manager: {APIKeyManager.__name__}\n"
                f"  - Token Manager: {TokenManager.__name__}\n"
                f"  - Token Validator: {TokenValidator.__name__}\n"
                f"  - Permission Registry: {PermissionRegistry.__name__}"
            ),
        },
        "status": {
            "help": "Show current authentication status",
            "handler": lambda **kwargs: print(
                "Auth Status:\n"
                "  Authenticator: available\n"
                "  API Key Manager: available\n"
                "  Token Manager: available\n"
                "  Permission Registry: available"
            ),
        },
    }


__all__ = [
    "Authenticator",
    "Token",
    "TokenManager",
    "APIKeyManager",
    "PermissionRegistry",
    "TokenValidator",
    "authenticate",
    "authorize",
    "get_authenticator",
    "cli_commands",
]

__version__ = "0.1.0"


from codomyrmex.exceptions import AuthenticationError


def authenticate(credentials: dict) -> Token | None:
    """Authenticate with credentials."""
    authenticator = Authenticator()
    return authenticator.authenticate(credentials)


def authorize(token: Token, resource: str, permission: str) -> bool:
    """Check if token has permission."""
    authenticator = Authenticator()
    return authenticator.authorize(token, resource, permission)


def get_authenticator() -> Authenticator:
    """Get an authenticator instance."""
    return Authenticator()


