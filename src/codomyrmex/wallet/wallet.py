"""Wallet Module - Facade.

Provides a simplified interface combining WalletManager and
NaturalRitualRecovery into a single unified wallet object.
"""

from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

from .core import WalletManager
from .recovery import NaturalRitualRecovery, RitualStep

logger = get_logger(__name__)


class Wallet:
    """Unified wallet combining key management and recovery.

    Provides a single entry point for wallet operations that delegates
    to WalletManager for key operations and NaturalRitualRecovery
    for recovery flows.
    """

    def __init__(
        self,
        user_id: str,
        storage_path: Path | None = None,
    ):
        """Initialize a Wallet for a specific user.

        Args:
            user_id: The owner's unique identifier.
            storage_path: Optional directory for key storage.
        """
        self.user_id = user_id
        self._manager = WalletManager(storage_path=storage_path)
        self._recovery = NaturalRitualRecovery()
        self._address: str | None = None
        logger.info(f"Wallet initialized for user {user_id}")

    @property
    def address(self) -> str | None:
        """The wallet address, or None if not yet created."""
        return self._address

    @property
    def is_active(self) -> bool:
        """Whether this wallet has been created and is active."""
        return self._address is not None

    def create(self) -> str:
        """Create the wallet and return the address.

        Returns:
            The generated wallet address.
        """
        self._address = self._manager.create_wallet(self.user_id)
        return self._address

    def sign(self, message: bytes) -> bytes:
        """Sign a message.

        Args:
            message: Message bytes to sign.

        Returns:
            Signature bytes.
        """
        return self._manager.sign_message(self.user_id, message)

    def verify(self, message: bytes, signature: bytes) -> bool:
        """Verify a message signature.

        Args:
            message: Original message bytes.
            signature: Signature to verify.

        Returns:
            True if valid.
        """
        return self._manager.verify_signature(self.user_id, message, signature)

    def rotate(self, reason: str = "manual") -> str:
        """Rotate the wallet's keys.

        Args:
            reason: Reason for rotation.

        Returns:
            New wallet address.
        """
        self._address = self._manager.rotate_keys(self.user_id, reason=reason)
        return self._address

    def setup_recovery(self, steps: list[RitualStep]) -> None:
        """Register recovery ritual steps.

        Args:
            steps: List of RitualStep objects defining the recovery ritual.
        """
        self._recovery.register_ritual(self.user_id, steps)

    def recover(self, responses: list[str]) -> bool:
        """Attempt recovery via natural ritual.

        Args:
            responses: Answers to ritual prompts.

        Returns:
            True if recovery succeeded.
        """
        return self._recovery.initiate_recovery(self.user_id, responses)

    def backup(self) -> dict[str, Any]:
        """Create a backup snapshot.

        Returns:
            Backup metadata dict.
        """
        return self._manager.backup_wallet(self.user_id)

    def delete(self) -> bool:
        """Delete this wallet and its keys.

        Returns:
            True if deletion succeeded.
        """
        result = self._manager.delete_wallet(self.user_id)
        if result:
            self._address = None
            self._recovery.unregister_ritual(self.user_id)
        return result
