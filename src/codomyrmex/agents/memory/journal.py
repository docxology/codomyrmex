"""Agent learning journal with pattern detection."""

from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class JournalEntry:
    """A learning journal entry.

    Attributes:
        topic: What was learned.
        insight: The insight or lesson.
        source: Where it came from.
        confidence: Confidence level (0-1).
        tags: Categorization tags.
        timestamp: When recorded.
    """

    topic: str
    insight: str = ""
    source: str = ""
    confidence: float = 1.0
    tags: list[str] = field(default_factory=list)
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "topic": self.topic,
            "insight": self.insight,
            "source": self.source,
            "confidence": self.confidence,
            "tags": self.tags,
        }


class LearningJournal:
    """Track agent learning with pattern detection.

    Usage::

        journal = LearningJournal()
        journal.record("python", "Use list comprehensions for clarity")
        patterns = journal.detect_patterns()
    """

    def __init__(self) -> None:
        self._entries: list[JournalEntry] = []

    def record(
        self,
        topic: str,
        insight: str = "",
        source: str = "",
        confidence: float = 1.0,
        tags: list[str] | None = None,
    ) -> JournalEntry:
        """Record."""
        entry = JournalEntry(
            topic=topic, insight=insight, source=source,
            confidence=confidence, tags=tags or [],
        )
        self._entries.append(entry)
        return entry

    @property
    def size(self) -> int:
        """Size."""
        return len(self._entries)

    def by_topic(self, topic: str) -> list[JournalEntry]:
        return [e for e in self._entries if e.topic == topic]

    def by_tag(self, tag: str) -> list[JournalEntry]:
        return [e for e in self._entries if tag in e.tags]

    def detect_patterns(self) -> dict[str, Any]:
        """Detect recurring topics and tags."""
        topic_counts = Counter(e.topic for e in self._entries)
        tag_counts = Counter(tag for e in self._entries for tag in e.tags)
        return {
            "top_topics": topic_counts.most_common(5),
            "top_tags": tag_counts.most_common(5),
            "total_entries": self.size,
            "avg_confidence": (
                sum(e.confidence for e in self._entries) / self.size
                if self.size > 0 else 0.0
            ),
        }

    def recent(self, n: int = 10) -> list[JournalEntry]:
        """Recent."""
        return self._entries[-n:]

    def high_confidence(self, threshold: float = 0.8) -> list[JournalEntry]:
        return [e for e in self._entries if e.confidence >= threshold]


__all__ = ["JournalEntry", "LearningJournal"]
