"""Google Auth submodule for Codomyrmex.

Provides unified Google OAuth2 token acquisition and caching 
for downstream integrations like Calendar and Gmail.
"""

from .authenticator import GoogleAuthenticator, DEFAULT_SCOPES, AUTH_AVAILABLE

__all__ = ["GoogleAuthenticator", "DEFAULT_SCOPES", "AUTH_AVAILABLE"]
