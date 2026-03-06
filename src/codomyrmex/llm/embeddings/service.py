"""EmbeddingCache, EmbeddingIndex, EmbeddingService, and chunk_text utility."""

import hashlib
import threading
from collections.abc import Callable
from typing import Any

from .models import Embedding, SimilarityResult
from .providers import EmbeddingProvider
from .similarity import cosine_similarity


class EmbeddingCache:
    """
    Cache for embeddings to avoid regeneration.

    Usage:
        cache = EmbeddingCache()
        embedding = cache.get("hello world", "ada-002")
        if embedding is None:
            embedding = provider.embed("hello world")
            cache.set(embedding)
    """

    def __init__(self, max_size: int = 10000):
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


class EmbeddingIndex:
    """
    Simple in-memory embedding index for similarity search.

    Usage:
        index = EmbeddingIndex()
        index.add(embedding1)
        index.add_batch([embedding2, embedding3])
        results = index.search(query_embedding, k=5)
        for result in results:
            print(f"{result.text}: {result.score}")
    """

    def __init__(
        self,
        similarity_fn: Callable[[list[float], list[float]], float] = cosine_similarity,
    ):
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
        query: "Embedding | list[float]",
        k: int = 10,
        threshold: float | None = None,
    ) -> list[SimilarityResult]:
        """Search for similar embeddings."""
        query_vector = query.vector if isinstance(query, Embedding) else query

        results = []
        with self._lock:
            for emb in self._embeddings:
                score = self.similarity_fn(query_vector, emb.vector)
                if threshold is None or score >= threshold:
                    results.append(SimilarityResult(embedding=emb, score=score))

        results.sort(key=lambda r: r.score, reverse=True)
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
        embedding = service.embed("Hello world")
        embeddings = service.embed_texts(["text1", "text2", "text3"])
    """

    def __init__(
        self,
        provider: EmbeddingProvider,
        cache: EmbeddingCache | None = None,
        batch_size: int = 100,
    ):
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
        """Generate embedding for text."""
        self._stats["total_requests"] += 1

        if use_cache:
            cached = self.cache.get(text, self.provider.model_name)
            if cached:
                self._stats["cache_hits"] += 1
                return cached

        self._stats["api_calls"] += 1
        embedding = self.provider.embed(text)

        if metadata:
            embedding.metadata.update(metadata)

        if use_cache:
            self.cache.set(embedding)

        return embedding

    def embed_texts(
        self,
        texts: list[str],
        use_cache: bool = True,
    ) -> list[Embedding]:
        """Generate embeddings for multiple texts, using cache and batching."""
        results: dict[int, Embedding] = {}
        uncached: list[tuple[int, str]] = []

        for i, text in enumerate(texts):
            self._stats["total_requests"] += 1

            if use_cache:
                cached = self.cache.get(text, self.provider.model_name)
                if cached:
                    self._stats["cache_hits"] += 1
                    results[i] = cached
                    continue

            uncached.append((i, text))

        for batch_start in range(0, len(uncached), self.batch_size):
            batch = uncached[batch_start : batch_start + self.batch_size]
            batch_texts = [text for _, text in batch]

            self._stats["api_calls"] += 1
            embeddings = self.provider.embed_batch(batch_texts)

            for (idx, _), embedding in zip(batch, embeddings, strict=False):
                results[idx] = embedding
                if use_cache:
                    self.cache.set(embedding)

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
    """Split text into chunks for embedding."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunks.append(text[start:])
            break

        sep_pos = text.rfind(separator, start + chunk_size // 2, end)
        if sep_pos > start:
            end = sep_pos + len(separator)

        chunks.append(text[start:end])
        start = end - overlap

    return chunks
