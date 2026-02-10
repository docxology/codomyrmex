"""
Vector Store Models

Data classes and distance metrics for vector similarity search.
"""

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SearchResult:
    """Result from vector similarity search."""
    id: str
    score: float
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other: "SearchResult") -> bool:
        return self.score < other.score


@dataclass
class VectorEntry:
    """A vector entry in the store."""
    id: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return len(self.embedding)


class DistanceMetric:
    """Distance metrics for similarity computation."""

    @staticmethod
    def cosine(vec1: list[float], vec2: list[float]) -> float:
        """Cosine similarity (returns 0-1, higher = more similar)."""
        if len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(x * x for x in vec1))
        mag2 = math.sqrt(sum(x * x for x in vec2))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)

    @staticmethod
    def euclidean(vec1: list[float], vec2: list[float]) -> float:
        """Euclidean distance (returns 0+, lower = more similar)."""
        if len(vec1) != len(vec2):
            return float('inf')
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

    @staticmethod
    def dot_product(vec1: list[float], vec2: list[float]) -> float:
        """Dot product similarity."""
        if len(vec1) != len(vec2):
            return 0.0
        return sum(a * b for a, b in zip(vec1, vec2))


def normalize_embedding(embedding: list[float]) -> list[float]:
    """Normalize an embedding to unit length."""
    magnitude = math.sqrt(sum(x * x for x in embedding))
    if magnitude == 0:
        return embedding
    return [x / magnitude for x in embedding]
