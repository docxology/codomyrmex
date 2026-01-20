"""
Authentication module for Codomyrmex.

This module provides authentication and authorization with API key management,
OAuth integration, and access control.
"""

from typing import Optional

from codomyrmex.exceptions import CodomyrmexError

from .api_key_manager import APIKeyManager
from .authenticator import Authenticator
from .token import Token, TokenManager
from .permissions import PermissionRegistry
from .validator import TokenValidator

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
]

__version__ = "0.1.0"


class AuthenticationError(CodomyrmexError):
    """Raised when authentication operations fail."""

    pass


def authenticate(credentials: dict) -> Optional[Token]:
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


