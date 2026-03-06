"""Embedding data models: EmbeddingModel enum, Embedding dataclass, SimilarityResult."""

import hashlib
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EmbeddingModel(Enum):
    """Available embedding models."""

    OPENAI_ADA_002 = "text-embedding-ada-002"
    OPENAI_3_SMALL = "text-embedding-3-small"
    OPENAI_3_LARGE = "text-embedding-3-large"
    COHERE_EMBED_V3 = "embed-english-v3.0"
    VOYAGE_LARGE = "voyage-large-2"
    LOCAL_SENTENCE_TRANSFORMER = "all-MiniLM-L6-v2"

    @property
    def dimensions(self) -> int:
        """Get embedding dimensions for model."""
        dims = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "embed-english-v3.0": 1024,
            "voyage-large-2": 1536,
            "all-MiniLM-L6-v2": 384,
        }
        return dims.get(self.value, 1536)


@dataclass
class Embedding:
    """A text embedding with metadata."""

    vector: list[float]
    text: str
    model: str
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def dimensions(self) -> int:
        """Get number of dimensions."""
        return len(self.vector)

    @property
    def text_hash(self) -> str:
        """Get hash of source text."""
        return hashlib.md5(self.text.encode()).hexdigest()

    def normalize(self) -> "Embedding":
        """Return normalized embedding (L2 norm)."""
        magnitude = math.sqrt(sum(x * x for x in self.vector))
        if magnitude > 0:
            normalized = [x / magnitude for x in self.vector]
            return Embedding(
                vector=normalized,
                text=self.text,
                model=self.model,
                created_at=self.created_at,
                metadata=self.metadata,
            )
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vector": self.vector,
            "text": self.text,
            "model": self.model,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Embedding":
        """Create from dictionary."""
        return cls(
            vector=data["vector"],
            text=data["text"],
            model=data["model"],
            created_at=datetime.fromisoformat(
                data.get("created_at", datetime.now().isoformat())
            ),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SimilarityResult:
    """Result of a similarity search."""

    embedding: Embedding
    score: float
    rank: int = 0

    @property
    def text(self) -> str:
        """Text."""
        return self.embedding.text
