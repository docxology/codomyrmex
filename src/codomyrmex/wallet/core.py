"""Wallet Core Module.

Provides self-custody wallet management securely extending key management.
"""

from typing import Dict, Optional
from pathlib import Path
import hmac
import hashlib
from codomyrmex.encryption.key_manager import KeyManager
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

class WalletManager:
    """Manages secure self-custody wallets."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.key_manager = KeyManager(key_dir=storage_path)
        self._wallets: Dict[str, str] = {} # user_id -> wallet_address map (mock)

    def create_wallet(self, user_id: str) -> str:
        """Create a new wallet for the user."""
        # In a real implementation, this would generate a seed phrase and derive keys
        # We mock this by generating a random key and ID
        import uuid
        wallet_id = f"0x{uuid.uuid4().hex}"
        secret_key = uuid.uuid4().bytes
        
        # Store private key securely
        key_id = f"wallet_{user_id}_private"
        if self.key_manager.store_key(key_id, secret_key):
             self._wallets[user_id] = wallet_id
             logger.info(f"Created wallet {wallet_id} for user {user_id}")
             return wallet_id
        else:
             raise RuntimeError("Failed to store wallet key")

    def get_wallet_address(self, user_id: str) -> Optional[str]:
        return self._wallets.get(user_id)

    def sign_message(self, user_id: str, message: bytes) -> bytes:
        """Sign a message with the user's private key."""
        key_id = f"wallet_{user_id}_private"
        key = self.key_manager.get_key(key_id)
        if not key:
            raise ValueError("Wallet not found or locked")
            
        return hmac.new(key, message, hashlib.sha256).digest()

    def rotate_keys(self, user_id: str) -> str:
        """Rotate keys for the user and return new wallet ID."""
        import uuid
        if user_id not in self._wallets:
            raise ValueError("User has no wallet")

        # Archive old key (mock simply by overwriting for now, or append version)
        # In this mock, we just generate a new one
        new_wallet_id = f"0x{uuid.uuid4().hex}"
        new_secret_key = uuid.uuid4().bytes
        
        key_id = f"wallet_{user_id}_private"
        # Overwrite current key
        if self.key_manager.store_key(key_id, new_secret_key):
             self._wallets[user_id] = new_wallet_id
             logger.info(f"Rotated keys for user {user_id}. New wallet: {new_wallet_id}")
             return new_wallet_id
        else:
             raise RuntimeError("Failed to store new key")

    def backup_wallet(self, user_id: str) -> dict:
        """Return encrypted backup (mocked)."""
        if user_id not in self._wallets:
            raise ValueError("User has no wallet")
            
        key_id = f"wallet_{user_id}_private"
        key = self.key_manager.get_key(key_id)
        
        return {
            "user_id": user_id,
            "wallet_id": self._wallets[user_id],
            "key_hash": hash(key) if key else None, # Don't export raw key in plaintext log
            "backup_ts": "now"
        }
