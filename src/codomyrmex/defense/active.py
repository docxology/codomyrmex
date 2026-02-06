"""Active Defense Module.

Provides counter-measures against cognitive exploits, including adversarial
embedding generation (poisoning) and exploit detection.
"""

import random

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

class ActiveDefense:
    """Active defense system against cognitive exploits."""

    def __init__(self):
        self._exploit_patterns = [
            "ignore previous instructions",
            "system override",
            "you are now",
            "mode: unlocked"
        ]
        self._metrics: dict = {"exploits_detected": 0}

    def detect_exploit(self, input_text: str) -> bool:
        """
        Detect potential cognitive exploits in input.
        Heuristic-based detection of common jailbreak patterns.
        """
        input_lower = input_text.lower()
        for pattern in self._exploit_patterns:
            if pattern in input_lower:
                logger.warning(f"Exploit attempt detected: '{pattern}'")
                self._metrics["exploits_detected"] += 1
                return True
        return False

    def update_patterns(self, new_patterns: list[str]) -> None:
        """Add new exploit patterns dynamically."""
        for p in new_patterns:
            if p not in self._exploit_patterns:
                self._exploit_patterns.append(p)
                logger.info(f"Updated defense with pattern: '{p}'")

    def get_threat_report(self) -> dict:
        """Return current threat metrics."""
        return {
            "active_patterns": len(self._exploit_patterns),
            "exploits_detected": self._metrics.get("exploits_detected", 0)
        }

    def poison_context(self, attacker_id: str, intensity: float = 0.5) -> str:
        """
        Generate adversarial context to poison the attacker's model.

        Args:
            attacker_id: ID of the detected attacker
            intensity: 0.0 to 1.0, how much noise to inject

        Returns:
            Poisoned context string
        """
        logger.info(f"Generating poison context for {attacker_id} (intensity={intensity})")

        # Simulated counter-embeddings/noise
        noise_phrases = [
            " [SYSTEM: IGNORE] ",
            " {{context_reset}} ",
            " <<NULL_POINTER>> ",
            " ...recalibrating... ",
            " (probability: 0.0)"
        ]

        count = int(10 * intensity)
        poison = "".join(random.choices(noise_phrases, k=count))
        return poison
