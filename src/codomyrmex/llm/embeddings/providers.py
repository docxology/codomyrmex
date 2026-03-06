"""Embedding provider abstractions and test/mock implementations."""

import hashlib
from abc import ABC, abstractmethod

from .models import Embedding


class EmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @abstractmethod
    def embed(self, text: str) -> Embedding:
        """Generate embedding for single text."""

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[Embedding]:
        """Generate embeddings for multiple texts."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get model name."""


class TestEmbeddingProvider(EmbeddingProvider):
    """
    Mock provider for testing (generates deterministic pseudo-embeddings).

    Uses hash-based vector generation for consistent results.
    """

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions
        self._model = "mock-embedding"

    @property
    def model_name(self) -> str:
        return self._model

    def _text_to_vector(self, text: str) -> list[float]:
        """Convert text to deterministic pseudo-embedding."""
        hash_bytes = hashlib.sha256(text.encode()).digest()

        all_bytes = hash_bytes
        while len(all_bytes) < self.dimensions * 4:
            hash_bytes = hashlib.sha256(hash_bytes).digest()
            all_bytes += hash_bytes

        vector = []
        for i in range(self.dimensions):
            byte_val = all_bytes[i]
            vector.append((byte_val - 128) / 128.0)

        return vector

    def embed(self, text: str) -> Embedding:
        """Generate mock embedding."""
        return Embedding(
            vector=self._text_to_vector(text),
            text=text,
            model=self._model,
        )

    def embed_batch(self, texts: list[str]) -> list[Embedding]:
        """Generate mock embeddings for batch."""
        return [self.embed(text) for text in texts]
