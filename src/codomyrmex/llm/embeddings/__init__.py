"""
LLM Embeddings Module

Text embedding generation, caching, and similarity computation.
"""

__version__ = "0.1.0"

import hashlib
import json
import math
import threading
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union


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
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
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
        """text ."""
        return self.embedding.text


class EmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @abstractmethod
    def embed(self, text: str) -> Embedding:
        """Generate embedding for single text."""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[Embedding]:
        """Generate embeddings for multiple texts."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get model name."""
        pass


class TestEmbeddingProvider(EmbeddingProvider):
    """
    Mock provider for testing (generates deterministic pseudo-embeddings).

    Uses hash-based vector generation for consistent results.
    """

    def __init__(self, dimensions: int = 384):
        """Initialize this instance."""
        self.dimensions = dimensions
        self._model = "mock-embedding"

    @property
    def model_name(self) -> str:
        """model Name ."""
        return self._model

    def _text_to_vector(self, text: str) -> list[float]:
        """Convert text to deterministic pseudo-embedding."""
        # Use hash to generate consistent vector
        hash_bytes = hashlib.sha256(text.encode()).digest()

        # Generate more bytes if needed
        all_bytes = hash_bytes
        while len(all_bytes) < self.dimensions * 4:
            hash_bytes = hashlib.sha256(hash_bytes).digest()
            all_bytes += hash_bytes

        # Convert to floats between -1 and 1
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


class EmbeddingCache:
    """
    Cache for embeddings to avoid regeneration.

    Usage:
        cache = EmbeddingCache()

        # Check if cached
        embedding = cache.get("hello world", "ada-002")
        if embedding is None:
            embedding = provider.embed("hello world")
            cache.set(embedding)
    """

    def __init__(self, max_size: int = 10000):
        """Initialize this instance."""
        self.max_size = max_size
        self._cache: dict[str, Embedding] = {}
        self._access_order: list[str] = []
        self._lock = threading.Lock()

    def _make_key(self, text: str, model: str) -> str:
        """Create cache key from text and model."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{model}:{text_hash}"

    def get(self, text: str, model: str) -> Embedding | None:
        """Get cached embedding if available."""
        key = self._make_key(text, model)
        with self._lock:
            if key in self._cache:
                # Move to end (LRU)
                self._access_order.remove(key)
                self._access_order.append(key)
                return self._cache[key]
        return None

    def set(self, embedding: Embedding) -> None:
        """Cache an embedding."""
        key = self._make_key(embedding.text, embedding.model)
        with self._lock:
            if key in self._cache:
                self._access_order.remove(key)
            elif len(self._cache) >= self.max_size:
                # Evict oldest
                oldest = self._access_order.pop(0)
                del self._cache[oldest]

            self._cache[key] = embedding
            self._access_order.append(key)

    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()

    @property
    def size(self) -> int:
        """Get number of cached embeddings."""
        return len(self._cache)


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Returns value between -1 (opposite) and 1 (identical).
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Dimension mismatch: {len(vec1)} vs {len(vec2)}")

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(x * x for x in vec1))
    magnitude2 = math.sqrt(sum(x * x for x in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def euclidean_distance(vec1: list[float], vec2: list[float]) -> float:
    """
    Compute Euclidean distance between two vectors.

    Returns value >= 0 (0 means identical).
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Dimension mismatch: {len(vec1)} vs {len(vec2)}")

    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))


def dot_product(vec1: list[float], vec2: list[float]) -> float:
    """Compute dot product of two vectors."""
    if len(vec1) != len(vec2):
        raise ValueError(f"Dimension mismatch: {len(vec1)} vs {len(vec2)}")

    return sum(a * b for a, b in zip(vec1, vec2))


class EmbeddingIndex:
    """
    Simple in-memory embedding index for similarity search.

    Usage:
        index = EmbeddingIndex()

        # Add embeddings
        index.add(embedding1)
        index.add_batch([embedding2, embedding3])

        # Search
        results = index.search(query_embedding, k=5)
        for result in results:
            print(f"{result.text}: {result.score}")
    """

    def __init__(
        self,
        similarity_fn: Callable[[list[float], list[float]], float] = cosine_similarity,
    ):
        """Initialize this instance."""
        self.similarity_fn = similarity_fn
        self._embeddings: list[Embedding] = []
        self._lock = threading.Lock()

    def add(self, embedding: Embedding) -> None:
        """Add an embedding to the index."""
        with self._lock:
            self._embeddings.append(embedding)

    def add_batch(self, embeddings: list[Embedding]) -> None:
        """Add multiple embeddings."""
        with self._lock:
            self._embeddings.extend(embeddings)

    def search(
        self,
        query: Embedding | list[float],
        k: int = 10,
        threshold: float | None = None,
    ) -> list[SimilarityResult]:
        """
        Search for similar embeddings.

        Args:
            query: Query embedding or vector
            k: Maximum results to return
            threshold: Minimum similarity score (optional)

        Returns:
            List of similar embeddings with scores
        """
        query_vector = query.vector if isinstance(query, Embedding) else query

        results = []
        with self._lock:
            for emb in self._embeddings:
                score = self.similarity_fn(query_vector, emb.vector)
                if threshold is None or score >= threshold:
                    results.append(SimilarityResult(embedding=emb, score=score))

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)

        # Take top k and assign ranks
        results = results[:k]
        for i, result in enumerate(results):
            result.rank = i + 1

        return results

    def remove(self, text: str) -> int:
        """Remove embeddings by text. Returns count removed."""
        with self._lock:
            original_count = len(self._embeddings)
            self._embeddings = [e for e in self._embeddings if e.text != text]
            return original_count - len(self._embeddings)

    def clear(self) -> None:
        """Clear all embeddings."""
        with self._lock:
            self._embeddings.clear()

    @property
    def count(self) -> int:
        """Get number of indexed embeddings."""
        return len(self._embeddings)


class EmbeddingService:
    """
    High-level embedding service with caching and batching.

    Usage:
        service = EmbeddingService(provider=OpenAIEmbeddingProvider())

        # Single embedding
        embedding = service.embed("Hello world")

        # Batch (uses cache, batches uncached)
        embeddings = service.embed_texts(["text1", "text2", "text3"])

        # With metadata
        embedding = service.embed("query", metadata={"type": "query"})
    """

    def __init__(
        self,
        provider: EmbeddingProvider,
        cache: EmbeddingCache | None = None,
        batch_size: int = 100,
    ):
        """Initialize this instance."""
        self.provider = provider
        self.cache = cache or EmbeddingCache()
        self.batch_size = batch_size
        self._stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "api_calls": 0,
        }

    def embed(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
        use_cache: bool = True,
    ) -> Embedding:
        """
        Generate embedding for text.

        Args:
            text: Text to embed
            metadata: Optional metadata to attach
            use_cache: Whether to use cache

        Returns:
            Embedding
        """
        self._stats["total_requests"] += 1

        # Check cache
        if use_cache:
            cached = self.cache.get(text, self.provider.model_name)
            if cached:
                self._stats["cache_hits"] += 1
                return cached

        # Generate
        self._stats["api_calls"] += 1
        embedding = self.provider.embed(text)

        if metadata:
            embedding.metadata.update(metadata)

        # Cache
        if use_cache:
            self.cache.set(embedding)

        return embedding

    def embed_texts(
        self,
        texts: list[str],
        use_cache: bool = True,
    ) -> list[Embedding]:
        """
        Generate embeddings for multiple texts.

        Efficiently uses cache and batches uncached texts.
        """
        results: dict[int, Embedding] = {}
        uncached: list[tuple[int, str]] = []

        # Check cache for each
        for i, text in enumerate(texts):
            self._stats["total_requests"] += 1

            if use_cache:
                cached = self.cache.get(text, self.provider.model_name)
                if cached:
                    self._stats["cache_hits"] += 1
                    results[i] = cached
                    continue

            uncached.append((i, text))

        # Batch process uncached
        for batch_start in range(0, len(uncached), self.batch_size):
            batch = uncached[batch_start:batch_start + self.batch_size]
            batch_texts = [text for _, text in batch]

            self._stats["api_calls"] += 1
            embeddings = self.provider.embed_batch(batch_texts)

            for (idx, _), embedding in zip(batch, embeddings):
                results[idx] = embedding
                if use_cache:
                    self.cache.set(embedding)

        # Return in original order
        return [results[i] for i in range(len(texts))]

    @property
    def stats(self) -> dict[str, int]:
        """Get usage statistics."""
        return self._stats.copy()

    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate."""
        if self._stats["total_requests"] == 0:
            return 0.0
        return self._stats["cache_hits"] / self._stats["total_requests"]


def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50,
    separator: str = "\n",
) -> list[str]:
    """
    Split text into chunks for embedding.

    Args:
        text: Text to split
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks
        separator: Preferred split point

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunks.append(text[start:])
            break

        # Try to find separator near end
        sep_pos = text.rfind(separator, start + chunk_size // 2, end)
        if sep_pos > start:
            end = sep_pos + len(separator)

        chunks.append(text[start:end])
        start = end - overlap

    return chunks


__all__ = [
    # Enums
    "EmbeddingModel",
    # Data classes
    "Embedding",
    "SimilarityResult",
    # Providers
    "EmbeddingProvider",
    "TestEmbeddingProvider",
    # Core classes
    "EmbeddingCache",
    "EmbeddingIndex",
    "EmbeddingService",
    # Similarity functions
    "cosine_similarity",
    "euclidean_distance",
    "dot_product",
    # Utilities
    "chunk_text",
]
