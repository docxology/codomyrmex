"""Key management for encryption keys."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = get_logger(__name__)


class KeyManager:
    """Manager for encryption key storage and retrieval.

    Stores keys in individual files within a specified directory, with
    restrictive file permissions (0o600).
    """

    def __init__(self, key_dir: str | Path | None = None):
        """Initialize key manager.

        Args:
            key_dir: Directory for key storage (default: system temp / codomyrmex_keys).
        """
        self.key_dir = Path(key_dir or Path(tempfile.gettempdir()) / "codomyrmex_keys")
        self.key_dir.mkdir(parents=True, exist_ok=True)

    def store_key(self, key_id: str, key: bytes) -> bool:
        """Store an encryption key securely.

        Args:
            key_id: Unique key identifier.
            key: Key raw bytes to store.

        Returns:
            True if successful.

        Raises:
            IOError: If storage fails.
        """
        try:
            key_file = self.key_dir / f"{key_id}.key"
            with open(key_file, "wb") as f:
                f.write(key)
            # Set restrictive permissions (owner read/write only)
            key_file.chmod(0o600)
            logger.info("Stored key: %s", key_id)
            return True
        except Exception as e:
            logger.error("Error storing key '%s': %s", key_id, e)
            raise

    def get_key(self, key_id: str) -> bytes | None:
        """Retrieve a stored encryption key.

        Args:
            key_id: Unique key identifier.

        Returns:
            Stored key bytes if found, None otherwise.
        """
        try:
            key_file = self.key_dir / f"{key_id}.key"
            if not key_file.exists():
                return None

            with open(key_file, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error("Error retrieving key '%s': %s", key_id, e)
            raise

    def delete_key(self, key_id: str) -> bool:
        """Delete a stored encryption key.

        Args:
            key_id: Unique key identifier.

        Returns:
            True if deletion successful, False otherwise.
        """
        try:
            key_file = self.key_dir / f"{key_id}.key"
            if key_file.exists():
                key_file.unlink()
                logger.info("Deleted key: %s", key_id)
                return True
            return False
        except Exception as e:
            logger.error("Error deleting key '%s': %s", key_id, e)
            raise

    def list_keys(self) -> Sequence[str]:
        """List all stored key identifiers.

        Returns:
            Sorted list of key ID strings.
        """
        return sorted(p.stem for p in self.key_dir.glob("*.key"))

    def key_exists(self, key_id: str) -> bool:
        """Check whether a key exists without loading it.

        Args:
            key_id: Unique key identifier.

        Returns:
            True if the key file exists.
        """
        return (self.key_dir / f"{key_id}.key").exists()

    def rotate_key(self, key_id: str, new_key: bytes) -> bytes | None:
        """Rotate a key: store a new key and return the old one.

        Args:
            key_id: Unique key identifier to rotate.
            new_key: Replacement key bytes.

        Returns:
            The previous key bytes, or None if no prior key existed.
        """
        old_key = self.get_key(key_id)
        self.store_key(key_id, new_key)
        return old_key
