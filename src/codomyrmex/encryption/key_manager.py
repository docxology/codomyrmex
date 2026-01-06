"""
Key management for encryption keys.
"""

import json
import tempfile
from pathlib import Path
from typing import Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from .encryptor import Encryptor

logger = get_logger(__name__)


class KeyManager:
    """Manager for encryption key storage and retrieval."""

    def __init__(self, key_dir: Optional[Path] = None):
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

    def get_key(self, key_id: str) -> Optional[bytes]:
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

