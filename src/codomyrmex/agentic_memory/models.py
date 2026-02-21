"""Core data models for the agentic memory system.

Provides ``Memory``, ``MemoryType``, ``MemoryImportance``, and
``RetrievalResult`` — the foundational value objects used across
stores, agents, and consolidation.
"""

from __future__ import annotations

import enum
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


class MemoryType(enum.Enum):
    """Classification of a memory entry."""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemoryImportance(enum.Enum):
    """Importance level, orderable by ``.value``."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Memory:
    """A single memory entry with metadata and access tracking."""

    id: str
    content: str
    memory_type: MemoryType = MemoryType.EPISODIC
    importance: MemoryImportance = MemoryImportance.MEDIUM
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = 0.0

    # ── behaviour ────────────────────────────────────────────────

    def access(self) -> None:
        """Record an access event."""
        self.access_count += 1
        self.last_accessed = time.time()

    # ── serialisation ────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "importance": self.importance.value,
            "metadata": self.metadata,
            "tags": self.tags,
            "created_at": self.created_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Memory:
        """Reconstruct a ``Memory`` from a dict (reverse of :meth:`to_dict`)."""
        memory_type = data.get("memory_type", "episodic")
        if isinstance(memory_type, str):
            memory_type = MemoryType(memory_type)

        importance = data.get("importance", 2)
        if isinstance(importance, int):
            importance = MemoryImportance(importance)
        elif isinstance(importance, str):
            importance = MemoryImportance[importance.upper()]

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content=data.get("content", ""),
            memory_type=memory_type,
            importance=importance,
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            created_at=data.get("created_at", time.time()),
            access_count=data.get("access_count", 0),
            last_accessed=data.get("last_accessed", 0.0),
        )


@dataclass
class RetrievalResult:
    """Result of a memory recall/search operation."""

    memory: Memory
    relevance_score: float = 0.0
    recency_score: float = 0.0
    importance_score: float = 0.0

    @property
    def combined_score(self) -> float:
        """Weighted combination of the three sub-scores, clamped to [0, 1]."""
        raw = (
            0.5 * self.relevance_score
            + 0.3 * self.recency_score
            + 0.2 * self.importance_score
        )
        return max(0.0, min(1.0, raw))
