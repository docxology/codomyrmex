"""Natural Ritual Recovery Module.

Implements key recovery via 'Natural Ritual' - a multi-factor sequence
of secret experiences and memory proofs. Similar to zero-knowledge proofs
in that the verifier learns nothing about the secrets themselves, only
whether the prover knows them.
"""

import hashlib
from dataclasses import dataclass

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..exceptions import RitualError

logger = get_logger(__name__)


@dataclass
class RitualStep:
    """A single step in the recovery ritual.

    Attributes:
        prompt: The question or challenge presented to the user.
        expected_response_hash: SHA-256 hex digest of the correct response.
    """

    prompt: str
    expected_response_hash: str


def hash_response(response: str) -> str:
    """Hash a ritual response for storage or comparison.

    Args:
        response: The plaintext response to hash.

    Returns:
        SHA-256 hex digest of the response.
    """
    return hashlib.sha256(response.encode()).hexdigest()


class NaturalRitualRecovery:
    """Orchestrates the Natural Ritual recovery flow.

    Recovery is an all-or-nothing process: every step must be answered
    correctly for the ritual to succeed. Failed attempts are logged
    but do not reveal which step failed to the caller (only via logs).
    """

    def __init__(self):
        """Initialize this instance."""
        self._rituals: dict[str, list[RitualStep]] = {}
        self._attempt_counts: dict[str, int] = {}
        self._max_attempts: int = 5

    @property
    def max_attempts(self) -> int:
        """Maximum recovery attempts before lockout."""
        return self._max_attempts

    @max_attempts.setter
    def max_attempts(self, value: int) -> None:
        """max Attempts ."""
        if value < 1:
            raise ValueError("max_attempts must be at least 1")
        self._max_attempts = value

    def register_ritual(self, user_id: str, steps: list[RitualStep]) -> None:
        """Define the user's unique recovery ritual.

        Args:
            user_id: The user identifier.
            steps: Ordered list of ritual steps with hashed expected responses.

        Raises:
            RitualError: If steps list is empty.
        """
        if not steps:
            raise RitualError("Ritual must have at least one step")
        self._rituals[user_id] = steps
        self._attempt_counts[user_id] = 0
        logger.info(f"Registered natural ritual for {user_id} with {len(steps)} steps")

    def has_ritual(self, user_id: str) -> bool:
        """Check if a user has a registered ritual.

        Args:
            user_id: The user identifier.

        Returns:
            True if a ritual is registered.
        """
        return user_id in self._rituals

    def get_prompts(self, user_id: str) -> list[str]:
        """Get the ritual prompts for a user (without revealing hashes).

        Args:
            user_id: The user identifier.

        Returns:
            List of prompt strings.

        Raises:
            RitualError: If no ritual is registered.
        """
        if user_id not in self._rituals:
            raise RitualError(f"No ritual defined for user {user_id}")
        return [step.prompt for step in self._rituals[user_id]]

    def get_remaining_attempts(self, user_id: str) -> int:
        """Get remaining recovery attempts before lockout.

        Args:
            user_id: The user identifier.

        Returns:
            Number of remaining attempts.
        """
        used = self._attempt_counts.get(user_id, 0)
        return max(0, self._max_attempts - used)

    def is_locked(self, user_id: str) -> bool:
        """Check if a user is locked out from recovery attempts.

        Args:
            user_id: The user identifier.

        Returns:
            True if user has exhausted all attempts.
        """
        return self.get_remaining_attempts(user_id) <= 0

    def reset_attempts(self, user_id: str) -> None:
        """Reset the attempt counter for a user (admin operation).

        Args:
            user_id: The user identifier.
        """
        self._attempt_counts[user_id] = 0
        logger.info(f"Reset attempt counter for {user_id}")

    def initiate_recovery(self, user_id: str, responses: list[str]) -> bool:
        """Attempt recovery by enacting the ritual.

        All responses must match their expected hashes for recovery to succeed.
        Returns False without revealing which step failed.

        Args:
            user_id: The user identifier.
            responses: List of response strings, one per ritual step.

        Returns:
            True if all responses matched, False otherwise.

        Raises:
            RitualError: If user is locked out.
        """
        if user_id not in self._rituals:
            logger.error("No ritual defined for user")
            return False

        if self.is_locked(user_id):
            raise RitualError(f"User {user_id} is locked out after {self._max_attempts} attempts")

        steps = self._rituals[user_id]
        if len(responses) != len(steps):
            logger.warning("Ritual failed: Incorrect number of steps")
            self._attempt_counts[user_id] = self._attempt_counts.get(user_id, 0) + 1
            return False

        self._attempt_counts[user_id] = self._attempt_counts.get(user_id, 0) + 1

        for i, (step, response) in enumerate(zip(steps, responses)):
            response_hash = hashlib.sha256(response.encode()).hexdigest()
            if response_hash != step.expected_response_hash:
                logger.warning(f"Ritual failed at step {i + 1}: 'The memory was false'")
                return False

        logger.info("Natural Ritual completed successfully. Access granted.")
        # Reset attempts on success
        self._attempt_counts[user_id] = 0
        return True

    def unregister_ritual(self, user_id: str) -> bool:
        """Remove a user's registered ritual.

        Args:
            user_id: The user identifier.

        Returns:
            True if a ritual was removed.
        """
        if user_id in self._rituals:
            del self._rituals[user_id]
            self._attempt_counts.pop(user_id, None)
            logger.info(f"Unregistered ritual for {user_id}")
            return True
        return False
