#!/usr/bin/env python3
"""
Secret Management Module for Codomyrmex Configuration Management.

This module provides secure secret management, encryption, and key rotation
capabilities for configuration management.
"""

import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from cryptography.fernet import Fernet

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


class SecretManager:
    """Secure secret management system."""

    def __init__(self, key_file: Optional[str] = None):
        """Initialize secret manager.

        Args:
            key_file: Path to encryption key file
        """
        self.key_file = Path(key_file) if key_file else Path.home() / ".codomyrmex" / "secrets.key"
        self.key_file.parent.mkdir(parents=True, exist_ok=True)

        # Generate or load encryption key
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.key)

        self.fernet = Fernet(self.key)
        self._secrets: dict[str, dict[str, Any]] = {}

    def store_secret(self, name: str, value: str, metadata: Optional[dict[str, Any]] = None) -> str:
        """Store a secret securely.

        Args:
            name: Secret name
            value: Secret value
            metadata: Additional metadata

        Returns:
            Secret ID
        """
        secret_id = secrets.token_hex(16)

        secret_data = {
            "id": secret_id,
            "name": name,
            "value": self.fernet.encrypt(value.encode()).decode(),
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self._secrets[secret_id] = secret_data
        logger.info(f"Stored secret: {name}")

        return secret_id

    def get_secret(self, secret_id: str) -> Optional[str]:
        """Retrieve a secret by ID.

        Args:
            secret_id: Secret ID

        Returns:
            Secret value or None if not found
        """
        if secret_id not in self._secrets:
            return None

        encrypted_value = self._secrets[secret_id]["value"]
        return self.fernet.decrypt(encrypted_value.encode()).decode()

    def get_secret_by_name(self, name: str) -> Optional[str]:
        """Retrieve a secret by name.

        Args:
            name: Secret name

        Returns:
            Secret value or None if not found
        """
        for secret in self._secrets.values():
            if secret["name"] == name:
                encrypted_value = secret["value"]
                return self.fernet.decrypt(encrypted_value.encode()).decode()
        return None

    def list_secrets(self) -> list[dict[str, Any]]:
        """List all stored secrets (without values).

        Returns:
            List of secret metadata
        """
        return [
            {
                "id": secret["id"],
                "name": secret["name"],
                "created_at": secret["created_at"],
                "metadata": secret["metadata"]
            }
            for secret in self._secrets.values()
        ]

    def delete_secret(self, secret_id: str) -> bool:
        """Delete a secret.

        Args:
            secret_id: Secret ID

        Returns:
            True if deleted successfully
        """
        if secret_id in self._secrets:
            del self._secrets[secret_id]
            logger.info(f"Deleted secret: {secret_id}")
            return True
        return False

    def rotate_key(self) -> str:
        """Rotate the encryption key.

        Returns:
            New key ID
        """
        old_key = self.key
        self.key = Fernet.generate_key()

        with open(self.key_file, 'wb') as f:
            f.write(self.key)

        self.fernet = Fernet(self.key)

        # Re-encrypt all existing secrets
        for secret_id, secret in self._secrets.items():
            try:
                # Decrypt with old key
                old_fernet = Fernet(old_key)
                decrypted_value = old_fernet.decrypt(secret["value"].encode()).decode()

                # Re-encrypt with new key
                secret["value"] = self.fernet.encrypt(decrypted_value.encode()).decode()
            except Exception as e:
                logger.error(f"Failed to re-encrypt secret {secret_id}: {e}")

        new_key_id = secrets.token_hex(8)
        logger.info(f"Rotated encryption key: {new_key_id}")
        return new_key_id


def manage_secrets(operation: str, **kwargs) -> Any:
    """Manage secrets based on operation.

    Args:
        operation: Operation to perform ('store', 'get', 'list', 'delete', 'rotate')
        **kwargs: Operation-specific arguments

    Returns:
        Operation result
    """
    manager = SecretManager()

    if operation == "store":
        return manager.store_secret(kwargs.get("name"), kwargs.get("value"), kwargs.get("metadata"))
    elif operation == "get":
        return manager.get_secret(kwargs.get("secret_id"))
    elif operation == "get_by_name":
        return manager.get_secret_by_name(kwargs.get("name"))
    elif operation == "list":
        return manager.list_secrets()
    elif operation == "delete":
        return manager.delete_secret(kwargs.get("secret_id"))
    elif operation == "rotate":
        return manager.rotate_key()
    else:
        raise CodomyrmexError(f"Unknown secret operation: {operation}")


def encrypt_configuration(config: dict[str, Any], secret_keys: list[str]) -> dict[str, Any]:
    """Encrypt sensitive configuration values.

    Args:
        config: Configuration dictionary
        secret_keys: List of keys that should be encrypted

    Returns:
        Configuration with encrypted values
    """
    manager = SecretManager()
    encrypted_config = config.copy()

    for key in secret_keys:
        if key in encrypted_config and isinstance(encrypted_config[key], str):
            secret_id = manager.store_secret(f"config_{key}", encrypted_config[key])
            encrypted_config[key] = f"encrypted:{secret_id}"

    return encrypted_config
