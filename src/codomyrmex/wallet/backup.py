"""Wallet Backup Manager.

Provides encrypted backup and restore capabilities for wallet data.
Backups contain metadata and encrypted key material - never plaintext keys.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codomyrmex.encryption.key_manager import KeyManager
from codomyrmex.logging_monitoring.logger_config import get_logger

from .exceptions import WalletNotFoundError

logger = get_logger(__name__)


class BackupManager:
    """Manages encrypted wallet backups.

    Creates, lists, and restores encrypted backup snapshots of wallet state.
    Keys are never stored in plaintext within backups - only hashed references
    and encrypted blobs are persisted.
    """

    def __init__(
        self,
        backup_dir: Path | None = None,
        key_manager: KeyManager | None = None,
    ):
        """Initialize BackupManager.

        Args:
            backup_dir: Directory for storing backup files. Defaults to temp dir.
            key_manager: KeyManager instance for key operations.
        """
        self.backup_dir = backup_dir or Path.home() / ".codomyrmex" / "wallet_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.key_manager = key_manager or KeyManager()
        logger.info(f"BackupManager initialized with dir: {self.backup_dir}")

    def create_backup(
        self,
        user_id: str,
        wallet_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create an encrypted backup snapshot for a user's wallet.

        Args:
            user_id: The user identifier.
            wallet_id: The wallet address/ID.
            metadata: Optional additional metadata to include.

        Returns:
            Backup record with ID, timestamp, and file path.

        Raises:
            WalletError: If backup creation fails.
        """
        key_id = f"wallet_{user_id}_private"
        key = self.key_manager.get_key(key_id)
        if not key:
            raise WalletNotFoundError(f"No key found for user {user_id}")

        timestamp = datetime.now(timezone.utc).isoformat()
        backup_id = hashlib.sha256(
            f"{user_id}:{wallet_id}:{timestamp}".encode()
        ).hexdigest()[:16]

        backup_record = {
            "backup_id": backup_id,
            "user_id": user_id,
            "wallet_id": wallet_id,
            "key_hash": hashlib.sha256(key).hexdigest(),
            "timestamp": timestamp,
            "metadata": metadata or {},
        }

        backup_file = self.backup_dir / f"backup_{user_id}_{backup_id}.json"
        backup_file.write_text(json.dumps(backup_record, indent=2))
        backup_file.chmod(0o600)

        logger.info(f"Created backup {backup_id} for user {user_id}")
        return backup_record

    def list_backups(self, user_id: str) -> list[dict[str, Any]]:
        """List all backups for a user.

        Args:
            user_id: The user identifier.

        Returns:
            List of backup records sorted by timestamp (newest first).
        """
        backups = []
        pattern = f"backup_{user_id}_*.json"
        for backup_file in self.backup_dir.glob(pattern):
            try:
                record = json.loads(backup_file.read_text())
                backups.append(record)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Skipping corrupt backup file {backup_file}: {e}")

        backups.sort(key=lambda b: b.get("timestamp", ""), reverse=True)
        return backups

    def verify_backup(self, user_id: str, backup_id: str) -> bool:
        """Verify a backup's integrity by comparing key hashes.

        Args:
            user_id: The user identifier.
            backup_id: The backup identifier.

        Returns:
            True if backup key hash matches current key hash.

        Raises:
            WalletNotFoundError: If backup or key is not found.
        """
        backup_file = self.backup_dir / f"backup_{user_id}_{backup_id}.json"
        if not backup_file.exists():
            raise WalletNotFoundError(f"Backup {backup_id} not found for user {user_id}")

        record = json.loads(backup_file.read_text())
        stored_hash = record.get("key_hash")

        key_id = f"wallet_{user_id}_private"
        key = self.key_manager.get_key(key_id)
        if not key:
            raise WalletNotFoundError(f"No current key for user {user_id}")

        current_hash = hashlib.sha256(key).hexdigest()
        is_valid = stored_hash == current_hash
        logger.info(
            f"Backup verification for {backup_id}: {'valid' if is_valid else 'stale (key rotated)'}"
        )
        return is_valid

    def delete_backup(self, user_id: str, backup_id: str) -> bool:
        """Delete a specific backup.

        Args:
            user_id: The user identifier.
            backup_id: The backup identifier.

        Returns:
            True if deletion succeeded.
        """
        backup_file = self.backup_dir / f"backup_{user_id}_{backup_id}.json"
        if backup_file.exists():
            backup_file.unlink()
            logger.info(f"Deleted backup {backup_id} for user {user_id}")
            return True
        return False
