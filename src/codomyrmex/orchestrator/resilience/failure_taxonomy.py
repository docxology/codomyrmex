"""Failure taxonomy for self-healing orchestration.

Classifies errors into categories with associated recovery strategies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FailureCategory(Enum):
    """Categories of failures."""
    CONFIG_ERROR = "config_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DEPENDENCY_FAILURE = "dependency_failure"
    LOGIC_ERROR = "logic_error"
    TIMEOUT = "timeout"
    PERMISSION_ERROR = "permission_error"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Recovery strategies for each failure category."""
    RETRY = "retry"
    ADJUST_CONFIG = "adjust_config"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    SKIP = "skip"
    RESTART = "restart"


# Mapping from failure category to recommended recovery
RECOVERY_MAP: dict[FailureCategory, list[RecoveryStrategy]] = {
    FailureCategory.CONFIG_ERROR: [RecoveryStrategy.ADJUST_CONFIG, RecoveryStrategy.ESCALATE],
    FailureCategory.RESOURCE_EXHAUSTION: [RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK],
    FailureCategory.DEPENDENCY_FAILURE: [RecoveryStrategy.FALLBACK, RecoveryStrategy.RETRY],
    FailureCategory.LOGIC_ERROR: [RecoveryStrategy.ESCALATE],
    FailureCategory.TIMEOUT: [RecoveryStrategy.RETRY, RecoveryStrategy.SKIP],
    FailureCategory.PERMISSION_ERROR: [RecoveryStrategy.ESCALATE],
    FailureCategory.UNKNOWN: [RecoveryStrategy.RETRY, RecoveryStrategy.ESCALATE],
}


@dataclass
class ClassifiedError:
    """An error classified into the taxonomy.

    Attributes:
        category: Failure category.
        original_error: The original error string.
        suggested_strategies: Ordered recovery strategies.
        context: Additional context about the failure.
        confidence: Classification confidence (0-1).
    """

    category: FailureCategory
    original_error: str
    suggested_strategies: list[RecoveryStrategy] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

    def __post_init__(self) -> None:
        """post Init ."""
        if not self.suggested_strategies:
            self.suggested_strategies = list(RECOVERY_MAP.get(self.category, []))

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "category": self.category.value,
            "original_error": self.original_error,
            "strategies": [s.value for s in self.suggested_strategies],
            "confidence": self.confidence,
        }


def classify_error(error: Exception | str) -> ClassifiedError:
    """Classify an error into the failure taxonomy.

    Uses keyword heuristics on the error message.

    Args:
        error: The error to classify.

    Returns:
        ``ClassifiedError`` with category and recovery strategies.
    """
    msg = str(error).lower()

    if any(kw in msg for kw in ("config", "setting", "parameter", "invalid value")):
        return ClassifiedError(FailureCategory.CONFIG_ERROR, str(error))
    if any(kw in msg for kw in ("memory", "disk", "quota", "resource", "oom")):
        return ClassifiedError(FailureCategory.RESOURCE_EXHAUSTION, str(error))
    if any(kw in msg for kw in ("connection", "network", "dns", "import", "module")):
        return ClassifiedError(FailureCategory.DEPENDENCY_FAILURE, str(error))
    if any(kw in msg for kw in ("timeout", "timed out", "deadline")):
        return ClassifiedError(FailureCategory.TIMEOUT, str(error))
    if any(kw in msg for kw in ("permission", "denied", "forbidden", "unauthorized")):
        return ClassifiedError(FailureCategory.PERMISSION_ERROR, str(error))
    if any(kw in msg for kw in ("assertion", "type error", "key error", "index", "attribute")):
        return ClassifiedError(FailureCategory.LOGIC_ERROR, str(error))

    return ClassifiedError(FailureCategory.UNKNOWN, str(error), confidence=0.5)


__all__ = [
    "ClassifiedError",
    "FailureCategory",
    "RECOVERY_MAP",
    "RecoveryStrategy",
    "classify_error",
]
