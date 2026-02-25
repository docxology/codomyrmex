"""Vector Store Models — data classes and distance metrics.

Provides:
- VectorEntry: stored embedding with metadata and timestamps
- SearchResult: ranked similarity search result
- DistanceMetric: cosine, euclidean, dot product, Manhattan distance
- Utility functions: normalize, random embedding, batch similarity
"""

from __future__ import annotations

import math
import random as _random
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

    def __lt__(self, other: SearchResult) -> bool:
        """Execute   Lt   operations natively."""
        return self.score < other.score

    def __repr__(self) -> str:
        """Execute   Repr   operations natively."""
        return f"SearchResult(id={self.id!r}, score={self.score:.4f}, dim={len(self.embedding)})"


@dataclass
class VectorEntry:
    """A vector entry in the store."""

    id: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime | None = None

    @property
    def dimension(self) -> int:
        """Execute Dimension operations natively."""
        return len(self.embedding)

    @property
    def magnitude(self) -> float:
        """Execute Magnitude operations natively."""
        return math.sqrt(sum(x * x for x in self.embedding))

    def update_embedding(self, new_embedding: list[float]) -> None:
        """Update the embedding and set updated_at timestamp."""
        self.embedding = new_embedding
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dictionary."""
        return {
            "id": self.id,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "dimension": self.dimension,
            "magnitude": self.magnitude,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VectorEntry:
        """Deserialize from a dictionary."""
        return cls(
            id=data["id"],
            embedding=data["embedding"],
            metadata=data.get("metadata", {}),
        )


class DistanceMetric:
    """Distance metrics for vector similarity computation."""

    @staticmethod
    def cosine(vec1: list[float], vec2: list[float]) -> float:
        """Cosine similarity (0–1, higher = more similar)."""
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
        """Euclidean distance (0+, lower = more similar)."""
        if len(vec1) != len(vec2):
            return float("inf")
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

    @staticmethod
    def dot_product(vec1: list[float], vec2: list[float]) -> float:
        """Dot product similarity."""
        if len(vec1) != len(vec2):
            return 0.0
        return sum(a * b for a, b in zip(vec1, vec2))

    @staticmethod
    def manhattan(vec1: list[float], vec2: list[float]) -> float:
        """Manhattan (L1) distance."""
        if len(vec1) != len(vec2):
            return float("inf")
        return sum(abs(a - b) for a, b in zip(vec1, vec2))

    @staticmethod
    def chebyshev(vec1: list[float], vec2: list[float]) -> float:
        """Chebyshev (L∞) distance — max absolute difference."""
        if len(vec1) != len(vec2):
            return float("inf")
        return max(abs(a - b) for a, b in zip(vec1, vec2))


# ─── Utility Functions ──────────────────────────────────────────────────


def normalize_embedding(embedding: list[float]) -> list[float]:
    """Normalize an embedding to unit length (L2 normalization)."""
    magnitude = math.sqrt(sum(x * x for x in embedding))
    if magnitude == 0:
        return embedding
    return [x / magnitude for x in embedding]


def random_embedding(dim: int, seed: int | None = None) -> list[float]:
    """Generate a random unit-normalized embedding.

    Args:
        dim: Dimensionality of the embedding.
        seed: Optional seed for reproducibility.
    """
    rng = _random.Random(seed)
    raw = [rng.gauss(0, 1) for _ in range(dim)]
    return normalize_embedding(raw)


def batch_cosine_similarity(
    query: list[float], candidates: list[list[float]]
) -> list[float]:
    """Compute cosine similarity between a query and multiple candidates.

    Args:
        query: The query embedding.
        candidates: List of candidate embeddings.

    Returns:
        List of similarity scores (same order as candidates).
    """
    return [DistanceMetric.cosine(query, c) for c in candidates]


def embedding_centroid(embeddings: list[list[float]]) -> list[float]:
    """Compute the centroid (mean) of a list of embeddings.

    Returns:
        The element-wise mean embedding.
    """
    if not embeddings:
        return []
    dim = len(embeddings[0])
    centroid = [0.0] * dim
    for emb in embeddings:
        for i, v in enumerate(emb):
            centroid[i] += v
    n = len(embeddings)
    return [c / n for c in centroid]
