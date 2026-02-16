"""Backward-compatible shim -- delegates to config_management.secrets.secret_manager."""

from .secrets.secret_manager import (  # noqa: F401
    SecretManager,
    encrypt_configuration,
    manage_secrets,
)
