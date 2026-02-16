"""Secure secret management with encryption support.

Provides secret storage, retrieval, key rotation, and
configuration value encryption using Fernet symmetric encryption.
Requires the cryptography package.
"""

from .secret_manager import (
    SecretManager,
    encrypt_configuration,
    manage_secrets,
)

__all__ = [
    "SecretManager",
    "encrypt_configuration",
    "manage_secrets",
]
