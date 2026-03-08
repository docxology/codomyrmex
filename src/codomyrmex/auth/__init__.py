"""
Authentication module for Codomyrmex.

This module provides authentication and authorization with API key management,
OAuth integration, and Role-Based Access Control (RBAC).
"""

import contextlib
from typing import Any, Optional

from codomyrmex.exceptions import AuthenticationError, CodomyrmexError

from .core.authenticator import Authenticator
from .providers.api_key_manager import APIKeyManager
from .rbac.permissions import PermissionRegistry
from .tokens.token import Token, TokenManager
from .tokens.validator import TokenValidator

# Shared schemas for cross-module interop
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus


def authenticate(credentials: dict[str, Any]) -> Token | None:
    """Authenticate with credentials.

    Convenience function that uses the Authenticator singleton.
    """
    return Authenticator().authenticate(credentials)


def authorize(token: Token | str, resource: str, permission: str) -> bool:
    """Check if token has permission.

    Convenience function that uses the Authenticator singleton.
    """
    return Authenticator().authorize(token, resource, permission)


def get_authenticator() -> Authenticator:
    """Get the Authenticator singleton instance."""
    return Authenticator()


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


from .rotation import (
    AuditEvent,
    CredentialEntry,
    CredentialRotator,
    CredentialStore,
    InMemoryCredentialStore,
    RotationPolicy,
)

__all__ = [
    "APIKeyManager",
    "AuditEvent",
    "Authenticator",
    "CredentialEntry",
    "CredentialRotator",
    "CredentialStore",
    "InMemoryCredentialStore",
    "PermissionRegistry",
    "RotationPolicy",
    "Token",
    "TokenManager",
    "TokenValidator",
    "authenticate",
    "authorize",
    "cli_commands",
    "get_authenticator",
]

__version__ = "1.1.0"
