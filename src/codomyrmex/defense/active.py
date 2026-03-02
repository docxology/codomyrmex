"""Active Defense Module.

Provides counter-measures against cognitive exploits, including adversarial
embedding generation (poisoning), exploit detection, and honeytoken traps.
"""

import random
import threading
import uuid
from datetime import datetime

from codomyrmex.logging_monitoring.core.logger_config import get_logger

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
        self._metrics: dict = {"exploits_detected": 0, "honeytokens_triggered": 0}
        self._honeytokens: dict[str, dict] = {}
        self._honeytoken_lock = threading.Lock()

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
            "exploits_detected": self._metrics.get("exploits_detected", 0),
            "honeytokens_active": len(self._honeytokens),
            "honeytokens_triggered": self._metrics.get("honeytokens_triggered", 0),
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

    # ── Honeytoken subsystem ─────────────────────────────────────────

    def create_honeytoken(self, *, label: str = "", context: str = "") -> str:
        """Create a canary token embedded in content.

        When the token appears in unexpected input, it signals data
        exfiltration or injection replay.

        Args:
            label: Human-readable label for tracking.
            context: Additional context about where the token was planted.

        Returns:
            The honeytoken string (UUID-based).
        """
        token = f"HT-{uuid.uuid4().hex[:12].upper()}"
        with self._honeytoken_lock:
            self._honeytokens[token] = {
                "label": label or "unnamed",
                "context": context,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "triggered": False,
                "trigger_count": 0,
            }
        logger.info(f"Honeytoken created: {token} ({label})")
        return token

    def check_honeytoken(self, text: str) -> list[str]:
        """Scan text for any planted honeytokens.

        Args:
            text: Input text to scan.

        Returns:
            List of triggered honeytoken IDs.
        """
        triggered: list[str] = []
        with self._honeytoken_lock:
            for token, info in self._honeytokens.items():
                if token in text:
                    info["triggered"] = True
                    info["trigger_count"] += 1
                    info["last_triggered_at"] = datetime.utcnow().isoformat() + "Z"
                    self._metrics["honeytokens_triggered"] += 1
                    triggered.append(token)
                    logger.warning(
                        f"Honeytoken triggered: {token} ({info['label']}) — "
                        f"trigger #{info['trigger_count']}"
                    )
        return triggered

    def list_honeytokens(self) -> dict[str, dict]:
        """List all active honeytokens with their status."""
        with self._honeytoken_lock:
            return dict(self._honeytokens)

