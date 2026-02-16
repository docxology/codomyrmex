"""Core authentication and authorization components.

This subpackage provides the main Authenticator class and the
AuthenticationError exception for the auth module.
"""

from .authenticator import AuthenticationError, Authenticator

__all__ = [
    "Authenticator",
    "AuthenticationError",
]
