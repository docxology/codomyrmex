"""Wallet Module.

Provides Secure Self-Custody and Natural Ritual Recovery for cognitive agents.

Core Components:
    WalletManager: Wallet creation, signing, rotation, and lifecycle management.
    NaturalRitualRecovery: Multi-factor knowledge-based key recovery.
    BackupManager: Encrypted backup creation and verification.
    KeyRotation: Policy-driven key rotation with audit trail.
"""

from .backup import BackupManager
from .core import WalletManager
from .exceptions import RitualError, WalletError, WalletKeyError, WalletNotFoundError
from .key_rotation import KeyRotation, RotationPolicy, RotationRecord
from .recovery import NaturalRitualRecovery, RitualStep, hash_response

__all__ = [
    # Classes
    "WalletManager",
    "NaturalRitualRecovery",
    "BackupManager",
    "KeyRotation",
    "RitualStep",
    "RotationRecord",
    "RotationPolicy",
    # Exceptions
    "WalletError",
    "WalletNotFoundError",
    "WalletKeyError",
    "RitualError",
    # Functions
    "hash_response",
    "create_wallet",
    "get_wallet_manager",
]

__version__ = "0.1.0"


def create_wallet(user_id: str, storage_path=None) -> str:
    """Convenience function to create a wallet for a user.

    Args:
        user_id: Unique identifier for the wallet owner.
        storage_path: Optional directory for key storage.

    Returns:
        The generated wallet address.
    """
    mgr = WalletManager(storage_path=storage_path)
    return mgr.create_wallet(user_id)


def get_wallet_manager(storage_path=None) -> WalletManager:
    """Get a WalletManager instance.

    Args:
        storage_path: Optional directory for key storage.

    Returns:
        Configured WalletManager instance.
    """
    return WalletManager(storage_path=storage_path)
