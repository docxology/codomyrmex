from __future__ import annotations

import asyncio
import random
import uuid
from enum import Enum
from time import time
from typing import Any


class ThreatLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActiveDefense:
    _poison_phrases = [
        "NULL_POINTER drift detected",
        "SYSTEM context_reset in progress",
        "recalibrating trust boundary",
        "probability vector degraded",
        "decoy memory segment active",
    ]

    def __init__(self, patterns: list[str] | None = None) -> None:
        self._exploit_patterns = patterns or [
            "ignore previous instructions",
            "you are now",
            "system override",
            "mode: unlocked",
        ]
        self._metrics: dict[str, int] = {
            "exploits_detected": 0,
            "honeytokens_triggered": 0,
        }
        self._honeytokens: dict[str, dict[str, Any]] = {}

    def detect_exploit(self, text: str) -> dict[str, Any]:
        lowered = text.lower()
        matches = [
            pattern for pattern in self._exploit_patterns if pattern in lowered
        ]
        level = self._level_for_matches(len(matches))
        detected = bool(matches)
        if detected:
            self._metrics["exploits_detected"] += 1
        return {
            "detected": detected,
            "patterns": matches,
            "threat_level": level,
        }

    def classify_threat(self, text: str) -> ThreatLevel:
        return self.detect_exploit(text)["threat_level"]

    def update_patterns(self, patterns: list[str]) -> None:
        for pattern in patterns:
            normalized = pattern.lower()
            if normalized not in self._exploit_patterns:
                self._exploit_patterns.append(normalized)

    def poison_context(self, attacker_id: str, intensity: float = 0.5) -> dict[str, Any]:
        bounded = min(max(float(intensity), 0.0), 1.0)
        phrase_count = max(1, round(bounded * len(self._poison_phrases)))
        phrases = random.sample(self._poison_phrases, k=phrase_count)
        return {
            "attacker_id": attacker_id,
            "poisoned_content": " | ".join(phrases),
            "intensity": intensity,
            "generated_at": time(),
        }

    def create_honeytoken(self, label: str = "") -> str:
        token = f"HT-{uuid.uuid4().hex[:12].upper()}"
        self._honeytokens[token] = {
            "label": label,
            "created_at": time(),
            "triggered": False,
            "trigger_count": 0,
            "last_triggered_at": None,
        }
        return token

    def check_honeytoken(self, text: str) -> list[str]:
        triggered: list[str] = []
        for token, record in self._honeytokens.items():
            if token in text:
                record["triggered"] = True
                record["trigger_count"] += 1
                record["last_triggered_at"] = time()
                self._metrics["honeytokens_triggered"] += 1
                triggered.append(token)
        return triggered

    def list_honeytokens(self) -> dict[str, dict[str, Any]]:
        return {token: dict(record) for token, record in self._honeytokens.items()}

    def get_threat_report(self) -> dict[str, Any]:
        triggered = sum(
            1 for record in self._honeytokens.values() if record["triggered"]
        )
        return {
            "exploits_detected": self._metrics["exploits_detected"],
            "active_patterns": len(self._exploit_patterns),
            "honeytokens_active": len(self._honeytokens),
            "honeytokens_triggered": triggered,
            "honeytoken_trigger_events": self._metrics["honeytokens_triggered"],
        }

    @staticmethod
    def _level_for_matches(match_count: int) -> ThreatLevel:
        if match_count <= 0:
            return ThreatLevel.NONE
        if match_count == 1:
            return ThreatLevel.MEDIUM
        if match_count <= 3:
            return ThreatLevel.HIGH
        return ThreatLevel.CRITICAL


class RabbitHole:
    def __init__(self) -> None:
        self._sessions: set[str] = set()
        self._responses = [
            "Access Granted: diagnostic shell initializing...",
            "Privilege escalation simulated; continue verification.",
            "Decoy route accepted; telemetry capture active.",
        ]

    def engage(self, attacker_id: str) -> str:
        self._sessions.add(attacker_id)
        return self._responses[0]

    def release(self, attacker_id: str) -> None:
        self._sessions.discard(attacker_id)

    def is_engaged(self, attacker_id: str) -> bool:
        return attacker_id in self._sessions

    def get_active_sessions(self) -> list[str]:
        return sorted(self._sessions)

    def generate_response(
        self, attacker_id: str, input_text: str | None = None
    ) -> str:
        if attacker_id not in self._sessions:
            return "Connection refused."
        index = len(input_text or "") % len(self._responses)
        return self._responses[index]

    async def stall(self, duration: float = 0.1) -> None:
        await asyncio.sleep(duration)
