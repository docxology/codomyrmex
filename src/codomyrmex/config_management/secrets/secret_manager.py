import secrets
from datetime import datetime
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger

"""Secret Management Module for Codomyrmex Configuration Management."""


logger = get_logger(__name__)


class SecretManager:
    """Secure secret management system."""

    def __init__(self, key_file: str | None = None):
        """Initialize secret manager.

        Args:
            key_file: Path to encryption key file
        """
        self.key_file = (
            Path(key_file) if key_file else Path.home() / ".codomyrmex" / "secrets.key"
        )
        self.key_file.parent.mkdir(parents=True, exist_ok=True)

        # Generate or load encryption key
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(self.key)

        self.fernet = Fernet(self.key)
        self._secrets: dict[str, dict[str, Any]] = {}
        self._rotation_history: list[dict[str, Any]] = []

    def store_secret(
        self, name: str, value: str, metadata: dict[str, Any] | None = None
    ) -> str:
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
            "metadata": metadata or {},
        }

        self._secrets[secret_id] = secret_data
        logger.info("Stored secret: %s", name)

        return secret_id

    def get_secret(self, secret_id: str) -> str | None:
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

    def get_secret_by_name(self, name: str) -> str | None:
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
                "metadata": secret["metadata"],
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
            logger.info("Deleted secret: %s", secret_id)
            return True
        return False

    def rotate_key(self) -> str:
        """Rotate the encryption key.

        Returns:
            New key ID
        """
        old_key = self.key
        self.key = Fernet.generate_key()

        with open(self.key_file, "wb") as f:
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
                logger.error("Failed to re-encrypt secret %s: %s", secret_id, e)

        new_key_id = secrets.token_hex(8)
        logger.info("Rotated encryption key: %s", new_key_id)
        return new_key_id

    def rotate_secret(self, name: str, new_value: str) -> dict[str, Any]:
        """Rotate (replace) a named secret with a new value, keeping an audit trail.

        Args:
            name: Secret name to rotate.
            new_value: New secret value.

        Returns:
            Dict with ``secret_id``, ``rotated_at``, ``previous_id``.
        """
        previous_id: str | None = None
        for sid, secret in self._secrets.items():
            if secret["name"] == name:
                previous_id = sid
                break

        if previous_id is not None:
            self.delete_secret(previous_id)

        new_id = self.store_secret(
            name,
            new_value,
            metadata={
                "rotated_from": previous_id,
                "rotation_time": datetime.now().isoformat(),
            },
        )

        event = {
            "secret_name": name,
            "new_id": new_id,
            "previous_id": previous_id,
            "rotated_at": datetime.now().isoformat(),
        }
        self._rotation_history.append(event)
        logger.info("Rotated secret %r: %s → %s", name, previous_id, new_id)
        return event

    def get_rotation_history(self, name: str | None = None) -> list[dict[str, Any]]:
        """Get the rotation event log.

        Args:
            name: If provided, filter history to this secret name only.

        Returns:
            List of rotation event dicts.
        """
        if name is None:
            return list(self._rotation_history)
        return [e for e in self._rotation_history if e["secret_name"] == name]

    def check_key_age(self, name: str, max_age_days: int = 90) -> dict[str, Any]:
        """Check whether a secret exceeds the maximum age threshold.

        Args:
            name: Secret name.
            max_age_days: Maximum age in days before the secret is flagged.

        Returns:
            Dict with ``name``, ``age_days``, ``stale``, ``created_at``.
        """
        for secret in self._secrets.values():
            if secret["name"] == name:
                created = datetime.fromisoformat(secret["created_at"])
                age = (datetime.now() - created).days
                return {
                    "name": name,
                    "age_days": age,
                    "stale": age > max_age_days,
                    "created_at": secret["created_at"],
                    "max_age_days": max_age_days,
                }
        return {
            "name": name,
            "age_days": -1,
            "stale": False,
            "created_at": None,
            "max_age_days": max_age_days,
        }


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
        return manager.store_secret(
            kwargs.get("name"), kwargs.get("value"), kwargs.get("metadata")
        )
    if operation == "get":
        return manager.get_secret(kwargs.get("secret_id"))
    if operation == "get_by_name":
        return manager.get_secret_by_name(kwargs.get("name"))
    if operation == "list":
        return manager.list_secrets()
    if operation == "delete":
        return manager.delete_secret(kwargs.get("secret_id"))
    if operation == "rotate":
        return manager.rotate_key()
    raise CodomyrmexError(f"Unknown secret operation: {operation}")


def encrypt_configuration(
    config: dict[str, Any], secret_keys: list[str]
) -> dict[str, Any]:
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
