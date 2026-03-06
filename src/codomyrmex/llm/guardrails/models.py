"""Guardrail data models: ThreatLevel, GuardrailAction, GuardrailResult, GuardrailConfig."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ThreatLevel(Enum):
    """Threat severity levels."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GuardrailAction(Enum):
    """Actions to take when a guardrail is triggered."""

    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    SANITIZE = "sanitize"


@dataclass
class GuardrailResult:
    """Result of a guardrail check."""

    passed: bool
    threat_level: ThreatLevel = ThreatLevel.NONE
    action: GuardrailAction = GuardrailAction.ALLOW
    message: str = ""
    threats_detected: list[str] = field(default_factory=list)
    sanitized_content: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_safe(self) -> bool:
        """Check if content is safe to proceed."""
        return self.passed and self.action in [
            GuardrailAction.ALLOW,
            GuardrailAction.WARN,
        ]


@dataclass
class GuardrailConfig:
    """Configuration for guardrail behavior."""

    block_on_high_threat: bool = True
    block_on_medium_threat: bool = False
    sanitize_pii: bool = True
    max_input_length: int = 100000
    max_output_length: int = 500000
    custom_blocked_patterns: list[str] = field(default_factory=list)
    custom_allowed_patterns: list[str] = field(default_factory=list)
