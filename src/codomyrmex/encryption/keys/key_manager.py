"""
Key management for encryption keys.
"""

import tempfile
from pathlib import Path

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class KeyManager:
    """Manager for encryption key storage and retrieval."""

    def __init__(self, key_dir: Path | None = None):
        """Initialize key manager.

        Args:
            key_dir: Directory for key storage
        """
        self.key_dir = key_dir or Path(tempfile.gettempdir()) / "codomyrmex_keys"
        self.key_dir.mkdir(parents=True, exist_ok=True)

    def store_key(self, key_id: str, key: bytes) -> bool:
        """Store an encryption key securely.

        Args:
            key_id: Key identifier
            key: Key to store

        Returns:
            True if successful
        """
        try:
            key_file = self.key_dir / f"{key_id}.key"
            with open(key_file, "wb") as f:
                f.write(key)
            # Set restrictive permissions
            key_file.chmod(0o600)
            logger.info(f"Stored key: {key_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing key: {e}")
            return False

    def get_key(self, key_id: str) -> bytes | None:
        """Retrieve a stored encryption key.

        Args:
            key_id: Key identifier

        Returns:
            Stored key if found, None otherwise
        """
        try:
            key_file = self.key_dir / f"{key_id}.key"
            if not key_file.exists():
                return None

            with open(key_file, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error retrieving key: {e}")
            return None

    def delete_key(self, key_id: str) -> bool:
        """Delete a stored encryption key.

        Args:
            key_id: Key identifier

        Returns:
            True if deletion successful
        """
        try:
            key_file = self.key_dir / f"{key_id}.key"
            if key_file.exists():
                key_file.unlink()
                logger.info(f"Deleted key: {key_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting key: {e}")
            return False

    def list_keys(self) -> list[str]:
        """List all stored key identifiers.

        Returns:
            List of key ID strings
        """
        return sorted(p.stem for p in self.key_dir.glob("*.key"))

    def key_exists(self, key_id: str) -> bool:
        """Check whether a key exists without loading it.

        Args:
            key_id: Key identifier

        Returns:
            True if the key file exists
        """
        return (self.key_dir / f"{key_id}.key").exists()

    def rotate_key(self, key_id: str, new_key: bytes) -> bytes | None:
        """Rotate a key: store a new key and return the old one.

        The old key is returned so callers can re-encrypt data that was
        protected by the previous key.

        Args:
            key_id: Key identifier to rotate
            new_key: The replacement key bytes

        Returns:
            The previous key bytes, or None if no prior key existed
        """
        old_key = self.get_key(key_id)
        self.store_key(key_id, new_key)
        return old_key
