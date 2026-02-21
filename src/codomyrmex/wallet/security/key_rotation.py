"""Key Rotation Module.

Provides automated and manual key rotation for wallet keys with
audit trail and configurable rotation policies.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from collections.abc import Callable

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..exceptions import WalletNotFoundError

logger = get_logger(__name__)


@dataclass
class RotationRecord:
    """Record of a single key rotation event."""

    user_id: str
    old_wallet_id: str
    new_wallet_id: str
    timestamp: str
    reason: str = "scheduled"


@dataclass
class RotationPolicy:
    """Defines when and how keys should be rotated.

    Attributes:
        max_age_days: Maximum age of a key before rotation is recommended.
        max_signatures: Maximum number of signatures before rotation.
        auto_rotate: Whether to auto-rotate when thresholds are exceeded.
    """

    max_age_days: int = 90
    max_signatures: int = 10000
    auto_rotate: bool = False


class KeyRotation:
    """Manages key rotation lifecycle and audit trail.

    Tracks rotation history, enforces rotation policies, and provides
    hooks for pre/post rotation callbacks.
    """

    def __init__(self, policy: RotationPolicy | None = None):
        """Initialize KeyRotation manager.

        Args:
            policy: Rotation policy to enforce. Uses defaults if not provided.
        """
        self.policy = policy or RotationPolicy()
        self._history: dict[str, list[RotationRecord]] = {}
        self._signature_counts: dict[str, int] = {}
        self._creation_times: dict[str, datetime] = {}
        self._pre_rotate_hooks: list[Callable] = []
        self._post_rotate_hooks: list[Callable] = []
        logger.info(
            f"KeyRotation initialized: max_age={self.policy.max_age_days}d, "
            f"max_sigs={self.policy.max_signatures}"
        )

    def register_wallet(self, user_id: str, wallet_id: str) -> None:
        """Register a wallet for rotation tracking.

        Args:
            user_id: The user identifier.
            wallet_id: The wallet address/ID.
        """
        self._signature_counts[user_id] = 0
        self._creation_times[user_id] = datetime.now(timezone.utc)
        if user_id not in self._history:
            self._history[user_id] = []
        logger.info(f"Registered wallet {wallet_id} for rotation tracking")

    def record_signature(self, user_id: str) -> None:
        """Record that a signature was made, incrementing the counter.

        Args:
            user_id: The user identifier.
        """
        self._signature_counts[user_id] = self._signature_counts.get(user_id, 0) + 1

    def needs_rotation(self, user_id: str) -> bool:
        """Check if a wallet's keys need rotation based on policy.

        Args:
            user_id: The user identifier.

        Returns:
            True if rotation is recommended.
        """
        sig_count = self._signature_counts.get(user_id, 0)
        if sig_count >= self.policy.max_signatures:
            logger.info(f"User {user_id}: rotation needed (signatures={sig_count})")
            return True

        created = self._creation_times.get(user_id)
        if created:
            age = (datetime.now(timezone.utc) - created).days
            if age >= self.policy.max_age_days:
                logger.info(f"User {user_id}: rotation needed (age={age} days)")
                return True

        return False

    def record_rotation(
        self,
        user_id: str,
        old_wallet_id: str,
        new_wallet_id: str,
        reason: str = "scheduled",
    ) -> RotationRecord:
        """Record a completed key rotation event.

        Args:
            user_id: The user identifier.
            old_wallet_id: Previous wallet ID.
            new_wallet_id: New wallet ID after rotation.
            reason: Why the rotation occurred.

        Returns:
            The rotation record.
        """
        record = RotationRecord(
            user_id=user_id,
            old_wallet_id=old_wallet_id,
            new_wallet_id=new_wallet_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            reason=reason,
        )

        if user_id not in self._history:
            self._history[user_id] = []
        self._history[user_id].append(record)

        # Reset counters
        self._signature_counts[user_id] = 0
        self._creation_times[user_id] = datetime.now(timezone.utc)

        # Run post-rotate hooks
        for hook in self._post_rotate_hooks:
            try:
                hook(record)
            except Exception as e:
                logger.warning(f"Post-rotate hook failed: {e}")

        logger.info(f"Recorded rotation for {user_id}: {old_wallet_id} -> {new_wallet_id}")
        return record

    def get_rotation_history(self, user_id: str) -> list[RotationRecord]:
        """Get the rotation history for a user.

        Args:
            user_id: The user identifier.

        Returns:
            List of rotation records, oldest first.

        Raises:
            WalletNotFoundError: If user has no rotation history.
        """
        if user_id not in self._history:
            raise WalletNotFoundError(f"No rotation history for user {user_id}")
        return list(self._history[user_id])

    def add_pre_rotate_hook(self, hook: Callable) -> None:
        """Register a callback to run before key rotation.

        Args:
            hook: Callable that receives (user_id, old_wallet_id).
        """
        self._pre_rotate_hooks.append(hook)

    def add_post_rotate_hook(self, hook: Callable) -> None:
        """Register a callback to run after key rotation.

        Args:
            hook: Callable that receives a RotationRecord.
        """
        self._post_rotate_hooks.append(hook)
