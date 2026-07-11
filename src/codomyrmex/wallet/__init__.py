"""Wallet Module.

Provides Secure Self-Custody and Natural Ritual Recovery for cognitive agents.

Core Components:
    WalletManager: Wallet creation, signing, rotation, and lifecycle management.
    NaturalRitualRecovery: Multi-factor knowledge-based key recovery.
    BackupManager: Encrypted backup creation and verification.
    KeyRotation: Policy-driven key rotation with audit trail.


Submodules:
    contracts: Consolidated contracts capabilities."""

import contextlib

from . import contracts, security
from .core import WalletManager
from .exceptions import RitualError, WalletError, WalletKeyError, WalletNotFoundError
from .security.backup import BackupManager
from .security.key_rotation import KeyRotation, RotationPolicy, RotationRecord
from .security.recovery import NaturalRitualRecovery, RitualStep, hash_response
from .zk_proof import (
    CapabilityAttestation,
    SignedCapabilityProof,
    SignedCapabilityProofBuilder,
    ZKProof,
    ZKProofVerifier,
    generate_zk_proof,
    verify_zk_proof,
)

# Shared schemas for cross-module interop
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus


def cli_commands():
    """Return CLI commands for the wallet module."""
    return {
        "balance": {
            "help": "Show wallet balance for a given user",
            "args": ["--user-id"],
            "handler": lambda user_id=None: (
                print(f"Wallet balance lookup for: {user_id}")
                if user_id
                else print("Usage: wallet balance --user-id <USER_ID>")
            ),
        },
        "transactions": {
            "help": "list recent wallet transactions",
            "args": ["--user-id", "--limit"],
            "handler": lambda user_id=None, limit=10: print(
                f"Listing last {limit} transactions"
                + (f" for user {user_id}" if user_id else "")
            ),
        },
    }


__all__ = [
    "BackupManager",
    "CapabilityAttestation",
    "KeyRotation",
    "NaturalRitualRecovery",
    "RitualError",
    "RitualStep",
    "RotationPolicy",
    "RotationRecord",
    "SignedCapabilityProof",
    "SignedCapabilityProofBuilder",
    # Exceptions
    "WalletError",
    "WalletKeyError",
    # Classes
    "WalletManager",
    "WalletNotFoundError",
    "ZKProof",
    "ZKProofVerifier",
    # CLI integration
    "cli_commands",
    "contracts",
    "create_wallet",
    "generate_zk_proof",
    "get_wallet_manager",
    # Functions
    "hash_response",
    "security",
    "verify_zk_proof",
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
