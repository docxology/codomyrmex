"""
Agentic Memory Models

Data classes and enums for the memory system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MemoryType(Enum):
    """Types of agent memory."""
    EPISODIC = "episodic"  # Specific experiences
    SEMANTIC = "semantic"  # General knowledge
    PROCEDURAL = "procedural"  # Skills/procedures
    WORKING = "working"  # Short-term active memory


class MemoryImportance(Enum):
    """Importance levels for memories."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Memory:
    """A single memory unit."""
    id: str
    content: str
    memory_type: MemoryType = MemoryType.EPISODIC
    importance: MemoryImportance = MemoryImportance.MEDIUM
    embedding: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0

    @property
    def age_hours(self) -> float:
        """Get memory age in hours."""
        return (datetime.now() - self.created_at).total_seconds() / 3600

    @property
    def recency_score(self) -> float:
        """Get recency score (decays over time)."""
        hours_since_access = (datetime.now() - self.accessed_at).total_seconds() / 3600
        return 1.0 / (1.0 + hours_since_access)

    def access(self) -> None:
        """Record an access to this memory."""
        self.accessed_at = datetime.now()
        self.access_count += 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "importance": self.importance.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Memory":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=MemoryType(data.get("memory_type", "episodic")),
            importance=MemoryImportance(data.get("importance", 2)),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            accessed_at=datetime.fromisoformat(data.get("accessed_at", datetime.now().isoformat())),
            access_count=data.get("access_count", 0),
        )


@dataclass
class RetrievalResult:
    """Result of memory retrieval."""
    memory: Memory
    relevance_score: float
    recency_score: float
    importance_score: float

    @property
    def combined_score(self) -> float:
        """Get combined ranking score."""
        return (
            0.4 * self.relevance_score +
            0.3 * self.recency_score +
            0.3 * self.importance_score
        )
