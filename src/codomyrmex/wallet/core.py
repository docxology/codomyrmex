"""Wallet Core Module.

Provides self-custody wallet management securely extending key management.
"""

import hashlib
import hmac
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from codomyrmex.encryption.key_manager import KeyManager
from codomyrmex.logging_monitoring.logger_config import get_logger

from .exceptions import WalletError, WalletKeyError, WalletNotFoundError

logger = get_logger(__name__)


class WalletManager:
    """Manages secure self-custody wallets.

    Provides wallet creation, message signing, key rotation, and backup
    operations. Keys are stored via the encryption module's KeyManager
    and never exposed in plaintext.

    Attributes:
        key_manager: KeyManager instance for secure key storage.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize WalletManager.

        Args:
            storage_path: Directory for key storage. Uses temp dir if None.
        """
        self.key_manager = KeyManager(key_dir=storage_path)
        self._wallets: Dict[str, str] = {}  # user_id -> wallet_address
        self._created_at: Dict[str, str] = {}  # user_id -> ISO timestamp

    def create_wallet(self, user_id: str) -> str:
        """Create a new wallet for the user.

        Generates a wallet ID and securely stores a private key.

        Args:
            user_id: Unique identifier for the wallet owner.

        Returns:
            The generated wallet address (0x-prefixed hex string).

        Raises:
            WalletKeyError: If key storage fails.
            WalletError: If user already has a wallet.
        """
        if user_id in self._wallets:
            raise WalletError(f"User {user_id} already has a wallet")

        wallet_id = f"0x{uuid.uuid4().hex}"
        secret_key = uuid.uuid4().bytes

        key_id = f"wallet_{user_id}_private"
        if self.key_manager.store_key(key_id, secret_key):
            self._wallets[user_id] = wallet_id
            self._created_at[user_id] = datetime.now(timezone.utc).isoformat()
            logger.info(f"Created wallet {wallet_id} for user {user_id}")
            return wallet_id
        else:
            raise WalletKeyError(f"Failed to store wallet key for user {user_id}")

    def get_wallet_address(self, user_id: str) -> Optional[str]:
        """Retrieve wallet address for a user.

        Args:
            user_id: The user identifier.

        Returns:
            Wallet address if found, None otherwise.
        """
        return self._wallets.get(user_id)

    def has_wallet(self, user_id: str) -> bool:
        """Check if a user has a wallet.

        Args:
            user_id: The user identifier.

        Returns:
            True if user has a wallet.
        """
        return user_id in self._wallets

    def sign_message(self, user_id: str, message: bytes) -> bytes:
        """Sign a message with the user's private key.

        Uses HMAC-SHA256 for message authentication.

        Args:
            user_id: The user identifier.
            message: The message bytes to sign.

        Returns:
            The HMAC-SHA256 signature bytes.

        Raises:
            WalletNotFoundError: If user has no wallet or key is missing.
        """
        key_id = f"wallet_{user_id}_private"
        key = self.key_manager.get_key(key_id)
        if not key:
            raise WalletNotFoundError(f"Wallet not found or locked for user {user_id}")

        return hmac.new(key, message, hashlib.sha256).digest()

    def verify_signature(self, user_id: str, message: bytes, signature: bytes) -> bool:
        """Verify a message signature.

        Args:
            user_id: The user identifier.
            message: The original message bytes.
            signature: The signature to verify.

        Returns:
            True if the signature is valid.

        Raises:
            WalletNotFoundError: If user has no wallet or key is missing.
        """
        expected = self.sign_message(user_id, message)
        return hmac.compare_digest(expected, signature)

    def rotate_keys(self, user_id: str, reason: str = "manual") -> str:
        """Rotate keys for the user and return new wallet ID.

        Archives the old key by overwriting with new key material.

        Args:
            user_id: The user identifier.
            reason: Reason for rotation (for audit trail).

        Returns:
            New wallet address.

        Raises:
            WalletNotFoundError: If user has no wallet.
            WalletKeyError: If key storage fails.
        """
        if user_id not in self._wallets:
            raise WalletNotFoundError(f"User {user_id} has no wallet")

        new_wallet_id = f"0x{uuid.uuid4().hex}"
        new_secret_key = uuid.uuid4().bytes

        key_id = f"wallet_{user_id}_private"
        if self.key_manager.store_key(key_id, new_secret_key):
            old_id = self._wallets[user_id]
            self._wallets[user_id] = new_wallet_id
            self._created_at[user_id] = datetime.now(timezone.utc).isoformat()
            logger.info(
                f"Rotated keys for user {user_id}: {old_id} -> {new_wallet_id} ({reason})"
            )
            return new_wallet_id
        else:
            raise WalletKeyError(f"Failed to store new key for user {user_id}")

    def backup_wallet(self, user_id: str) -> dict:
        """Return backup metadata for a user's wallet.

        The backup contains metadata and a key hash only - never raw keys.

        Args:
            user_id: The user identifier.

        Returns:
            Backup metadata dict with user_id, wallet_id, key_hash, timestamp.

        Raises:
            WalletNotFoundError: If user has no wallet.
        """
        if user_id not in self._wallets:
            raise WalletNotFoundError(f"User {user_id} has no wallet")

        key_id = f"wallet_{user_id}_private"
        key = self.key_manager.get_key(key_id)

        return {
            "user_id": user_id,
            "wallet_id": self._wallets[user_id],
            "key_hash": hashlib.sha256(key).hexdigest() if key else None,
            "created_at": self._created_at.get(user_id),
            "backup_ts": datetime.now(timezone.utc).isoformat(),
        }

    def delete_wallet(self, user_id: str) -> bool:
        """Delete a user's wallet and associated key.

        Args:
            user_id: The user identifier.

        Returns:
            True if deletion succeeded.

        Raises:
            WalletNotFoundError: If user has no wallet.
        """
        if user_id not in self._wallets:
            raise WalletNotFoundError(f"User {user_id} has no wallet")

        key_id = f"wallet_{user_id}_private"
        self.key_manager.delete_key(key_id)
        del self._wallets[user_id]
        self._created_at.pop(user_id, None)
        logger.info(f"Deleted wallet for user {user_id}")
        return True

    def list_wallets(self) -> Dict[str, str]:
        """List all registered wallets.

        Returns:
            Dictionary mapping user_id to wallet_address.
        """
        return dict(self._wallets)
