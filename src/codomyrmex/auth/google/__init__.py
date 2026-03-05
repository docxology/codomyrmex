"""Google Auth submodule for Codomyrmex.

Provides unified Google OAuth2 token acquisition and caching
for downstream integrations like Calendar and Gmail.
"""

from .authenticator import AUTH_AVAILABLE, DEFAULT_SCOPES, GoogleAuthenticator

__all__ = ["AUTH_AVAILABLE", "DEFAULT_SCOPES", "GoogleAuthenticator"]
