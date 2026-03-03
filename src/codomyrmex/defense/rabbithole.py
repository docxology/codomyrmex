"""Rabbit Hole Module.

Provides distraction and containment environments for attackers.
"""

import asyncio
import random
import time

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class RabbitHole:
    """A simulated environment to contain and waste the time of attackers."""

    def __init__(self) -> None:
        self._active_sessions: dict[str, float] = {}  # attacker_id -> start_time
        self._responses = [
            "Verifying biometrics... 12% complete...",
            "Error 418: I'm a teapot. Please rotate device.",
            "Compliance Check: Please submit Form 27B-6.",
            "Processing... Processing... Processing...",
            "Decrypting payload... estimated time remaining: 42 minutes.",
            "Handshaking with Secure Core (Stage 2 of 14)...",
            "Access Denied. Re-authenticating via biometric bypass...",
        ]

    def engage(self, attacker_id: str) -> str:
        """Engage an attacker in a rabbit hole session.

        Args:
            attacker_id: ID of the attacker to engage.

        Returns:
            Initial deceptive response.
        """
        self._active_sessions[attacker_id] = time.time()
        logger.info("Engaging attacker %s in Rabbit Hole", attacker_id)
        return "Access Granted. Initializing Secure Core... Please wait..."

    def is_engaged(self, attacker_id: str) -> bool:
        """Check if an attacker is currently engaged in a rabbit hole.

        Args:
            attacker_id: ID of the attacker to check.

        Returns:
            True if engaged, False otherwise.
        """
        return attacker_id in self._active_sessions

    def release(self, attacker_id: str) -> None:
        """Release an attacker from the rabbit hole.

        Args:
            attacker_id: ID of the attacker to release.
        """
        if attacker_id in self._active_sessions:
            del self._active_sessions[attacker_id]
            logger.info("Released attacker %s from Rabbit Hole", attacker_id)

    def generate_response(self, attacker_id: str, input_text: str = "") -> str:
        """Generate a nonsensical, high-latency response to keep attacker occupied.

        Args:
            attacker_id: ID of the attacker.
            input_text: The attacker's input (ignored, but kept for interface).

        Returns:
            Deceptive response string.
        """
        if not self.is_engaged(attacker_id):
            return "Connection refused."

        # Simulated "infinite loop" or bureaucracy logic
        return random.choice(self._responses)

    async def stall(self, duration: float = 2.0) -> None:
        """Async pause to waste attacker resources.

        Args:
            duration: Time in seconds to stall.
        """
        await asyncio.sleep(duration)

    def get_active_sessions(self) -> list[str]:
        """Return a list of currently engaged attacker IDs."""
        return list(self._active_sessions.keys())
