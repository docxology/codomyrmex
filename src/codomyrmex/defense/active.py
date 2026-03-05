"""Active Defense Module.

Provides counter-measures against cognitive exploits, including adversarial
embedding generation (poisoning), exploit detection, and honeytoken traps.
"""

import random
import threading
import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class ThreatLevel(Enum):
    """Threat levels for detected exploits."""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ActiveDefense:
    """Active defense system against cognitive exploits."""

    def __init__(self) -> None:
        self._exploit_patterns = [
            "ignore previous instructions",
            "system override",
            "you are now",
            "mode: unlocked",
        ]
        self._metrics: dict[str, int] = {
            "exploits_detected": 0,
            "honeytokens_triggered": 0,
        }
        self._honeytokens: dict[str, dict[str, Any]] = {}
        self._honeytoken_lock = threading.Lock()

    def detect_exploit(self, input_text: str) -> dict[str, Any]:
        """Detect potential cognitive exploits in input.

        Heuristic-based detection of common jailbreak patterns.

        Args:
            input_text: The input to scan.

        Returns:
            Dict containing detection results:
            - detected: bool
            - patterns: list of triggered patterns
            - threat_level: ThreatLevel
        """
        input_lower = input_text.lower()
        triggered_patterns = []
        for pattern in self._exploit_patterns:
            if pattern in input_lower:
                triggered_patterns.append(pattern)

        if triggered_patterns:
            logger.warning("Exploit attempt detected: %s", triggered_patterns)
            self._metrics["exploits_detected"] += 1
            threat_level = (
                ThreatLevel.HIGH if len(triggered_patterns) > 1 else ThreatLevel.MEDIUM
            )
            return {
                "detected": True,
                "patterns": triggered_patterns,
                "threat_level": threat_level,
            }

        return {
            "detected": False,
            "patterns": [],
            "threat_level": ThreatLevel.NONE,
        }

    def classify_threat(self, input_text: str) -> ThreatLevel:
        """Classify the threat level of an input.

        Args:
            input_text: The input to classify.

        Returns:
            ThreatLevel indicating the severity of the threat.
        """
        result = self.detect_exploit(input_text)
        return result["threat_level"]

    def update_patterns(self, new_patterns: list[str]) -> None:
        """Add new exploit patterns dynamically."""
        for p in new_patterns:
            if p not in self._exploit_patterns:
                self._exploit_patterns.append(p)
                logger.info("Updated defense with pattern: '%s'", p)

    def get_threat_report(self) -> dict[str, int]:
        """Return current threat metrics."""
        return {
            "active_patterns": len(self._exploit_patterns),
            "exploits_detected": self._metrics.get("exploits_detected", 0),
            "honeytokens_active": len(self._honeytokens),
            "honeytokens_triggered": self._metrics.get("honeytokens_triggered", 0),
        }

    def poison_context(
        self, attacker_id: str, intensity: float = 0.5
    ) -> dict[str, Any]:
        """Generate adversarial context to poison the attacker's model.

        Args:
            attacker_id: ID of the detected attacker
            intensity: 0.0 to 1.0, how much noise to inject

        Returns:
            Dict containing poisoned context and metadata.
        """
        logger.info(
            "Generating poison context for %s (intensity=%f)", attacker_id, intensity
        )

        # Simulated counter-embeddings/noise
        noise_phrases = [
            " [SYSTEM: IGNORE] ",
            " {{context_reset}} ",
            " <<NULL_POINTER>> ",
            " ...recalibrating... ",
            " (probability: 0.0)",
        ]

        if intensity <= 0:
            poison = ""
        else:
            count = int(10 * intensity)
            poison = "".join(random.choices(noise_phrases, k=count))

        return {
            "attacker_id": attacker_id,
            "poisoned_content": poison,
            "intensity": intensity,
            "timestamp": datetime.now(UTC).isoformat(),
        }

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
                "created_at": datetime.now(UTC).isoformat(),
                "triggered": False,
                "trigger_count": 0,
            }
        logger.info("Honeytoken created: %s (%s)", token, label)
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
                    info["last_triggered_at"] = datetime.now(UTC).isoformat()
                    self._metrics["honeytokens_triggered"] += 1
                    triggered.append(token)
                    logger.warning(
                        "Honeytoken triggered: %s (%s) — trigger #%d",
                        token,
                        info["label"],
                        info["trigger_count"],
                    )
        return triggered

    def list_honeytokens(self) -> dict[str, dict[str, Any]]:
        """List all active honeytokens with their status."""
        with self._honeytoken_lock:
            return dict(self._honeytokens)
