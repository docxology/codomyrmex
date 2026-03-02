"""Append-only healing event log.

Records diagnosis → recovery → outcome triples as structured events.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class HealingEvent:
    """A single healing event.

    Attributes:
        event_id: Unique event identifier.
        error_category: Failure category.
        diagnosis: Root cause summary.
        recovery_action: What recovery was attempted.
        outcome: Result (``success``, ``failure``, ``partial``).
        timestamp: Event timestamp.
        metadata: Additional details.
    """

    event_id: str = ""
    error_category: str = ""
    diagnosis: str = ""
    recovery_action: str = ""
    outcome: str = "pending"
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id:
            self.event_id = f"heal-{int(time.time() * 1000) % 100000}"
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "event_id": self.event_id,
            "error_category": self.error_category,
            "diagnosis": self.diagnosis,
            "recovery_action": self.recovery_action,
            "outcome": self.outcome,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict())


class HealingLog:
    """Append-only log of healing events.

    Stores diagnosis → recovery → outcome triples for learning.

    Usage::

        log = HealingLog()
        log.record(HealingEvent(
            error_category="timeout",
            diagnosis="API latency spike",
            recovery_action="Retry with increased timeout",
            outcome="success",
        ))
        print(log.success_rate)
    """

    def __init__(self) -> None:
        self._events: list[HealingEvent] = []

    def record(self, event: HealingEvent) -> None:
        """Append a healing event."""
        self._events.append(event)
        logger.info(
            "Healing event recorded",
            extra={"event_id": event.event_id, "outcome": event.outcome},
        )

    @property
    def size(self) -> int:
        """Size."""
        return len(self._events)

    @property
    def success_rate(self) -> float:
        """Rate of successful recoveries."""
        if not self._events:
            return 0.0
        successes = sum(1 for e in self._events if e.outcome == "success")
        return successes / len(self._events)

    def events_by_category(self, category: str) -> list[HealingEvent]:
        """Get events for a specific failure category."""
        return [e for e in self._events if e.error_category == category]

    def recent_events(self, limit: int = 10) -> list[HealingEvent]:
        """Get most recent events."""
        return list(self._events[-limit:])

    def summary(self) -> dict[str, Any]:
        """Get log summary statistics."""
        categories: dict[str, int] = {}
        outcomes: dict[str, int] = {}
        for e in self._events:
            categories[e.error_category] = categories.get(e.error_category, 0) + 1
            outcomes[e.outcome] = outcomes.get(e.outcome, 0) + 1
        return {
            "total_events": self.size,
            "success_rate": round(self.success_rate, 3),
            "by_category": categories,
            "by_outcome": outcomes,
        }

    def to_jsonl(self) -> str:
        """Export all events as JSONL string."""
        return "\n".join(e.to_jsonl() for e in self._events)


__all__ = [
    "HealingEvent",
    "HealingLog",
]
