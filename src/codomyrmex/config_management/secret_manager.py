# DEPRECATED(v0.2.0): Shim module. Import from config_management.secrets.secret_manager instead. Will be removed in v0.3.0.
"""Backward-compatible shim -- delegates to config_management.secrets.secret_manager."""

from .secrets.secret_manager import (  # noqa: F401
    SecretManager,
    encrypt_configuration,
    manage_secrets,
)
