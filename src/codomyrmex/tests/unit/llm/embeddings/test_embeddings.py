"""
Tests for LLM Embeddings Module
"""

import pytest

from codomyrmex.llm.embeddings import (
    Embedding,
    EmbeddingCache,
    EmbeddingIndex,
    EmbeddingService,
    TestEmbeddingProvider,
    chunk_text,
    cosine_similarity,
    dot_product,
    euclidean_distance,
)


class TestEmbedding:
    """Tests for Embedding class."""

    def test_create_embedding(self):
        """Should create embedding."""
        emb = Embedding(
            vector=[0.1, 0.2, 0.3],
            text="hello",
            model="test",
        )
        assert emb.dimensions == 3
        assert emb.text == "hello"

    def test_normalize(self):
        """Should normalize vector."""
        emb = Embedding(vector=[3.0, 4.0], text="test", model="test")
        normalized = emb.normalize()

        assert abs(normalized.vector[0] - 0.6) < 0.01
        assert abs(normalized.vector[1] - 0.8) < 0.01

    def test_to_dict(self):
        """Should convert to dict."""
        emb = Embedding(vector=[0.1, 0.2], text="test", model="model")
        data = emb.to_dict()

        assert data["text"] == "test"
        assert data["model"] == "model"
        assert data["vector"] == [0.1, 0.2]

    def test_from_dict(self):
        """Should create from dict."""
        emb = Embedding.from_dict({
            "vector": [0.1, 0.2],
            "text": "hello",
            "model": "test",
        })
        assert emb.text == "hello"
        assert emb.vector == [0.1, 0.2]


class TestMockProvider:
    """Tests for TestEmbeddingProvider."""

    def test_embed_single(self):
        """Should generate embedding."""
        provider = TestEmbeddingProvider(dimensions=128)
        emb = provider.embed("hello world")

        assert emb.dimensions == 128
        assert emb.text == "hello world"

    def test_embed_batch(self):
        """Should generate batch embeddings."""
        provider = TestEmbeddingProvider()
        embeddings = provider.embed_batch(["hello", "world"])

        assert len(embeddings) == 2
        assert embeddings[0].text == "hello"
        assert embeddings[1].text == "world"

    def test_deterministic(self):
        """Same text should produce same embedding."""
        provider = TestEmbeddingProvider()
        emb1 = provider.embed("test text")
        emb2 = provider.embed("test text")

        assert emb1.vector == emb2.vector


class TestSimilarityFunctions:
    """Tests for similarity functions."""

    def test_cosine_identical(self):
        """Identical vectors should have similarity 1."""
        vec = [0.5, 0.5, 0.5]
        assert abs(cosine_similarity(vec, vec) - 1.0) < 0.001

    def test_cosine_orthogonal(self):
        """Orthogonal vectors should have similarity 0."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        assert abs(cosine_similarity(vec1, vec2)) < 0.001

    def test_euclidean_identical(self):
        """Identical vectors should have distance 0."""
        vec = [0.5, 0.5]
        assert euclidean_distance(vec, vec) == 0.0

    def test_euclidean_distance(self):
        """Should compute correct distance."""
        vec1 = [0.0, 0.0]
        vec2 = [3.0, 4.0]
        assert abs(euclidean_distance(vec1, vec2) - 5.0) < 0.001

    def test_dot_product(self):
        """Should compute dot product."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [4.0, 5.0, 6.0]
        assert dot_product(vec1, vec2) == 32.0


class TestEmbeddingCache:
    """Tests for EmbeddingCache."""

    def test_cache_miss(self):
        """Should return None on miss."""
        cache = EmbeddingCache()
        result = cache.get("unknown", "model")
        assert result is None

    def test_cache_hit(self):
        """Should return cached embedding."""
        cache = EmbeddingCache()
        emb = Embedding(vector=[0.1], text="hello", model="test")
        cache.set(emb)

        cached = cache.get("hello", "test")
        assert isinstance(cached, Embedding)
        assert cached.text == "hello"

    def test_cache_eviction(self):
        """Should evict old entries when full."""
        cache = EmbeddingCache(max_size=2)

        for i in range(5):
            emb = Embedding(vector=[float(i)], text=f"text{i}", model="m")
            cache.set(emb)

        assert cache.size == 2


class TestEmbeddingIndex:
    """Tests for EmbeddingIndex."""

    def test_add_and_search(self):
        """Should find similar embeddings."""
        index = EmbeddingIndex()

        emb1 = Embedding(vector=[1.0, 0.0], text="east", model="test")
        emb2 = Embedding(vector=[0.0, 1.0], text="north", model="test")
        emb3 = Embedding(vector=[0.9, 0.1], text="east-ish", model="test")

        index.add_batch([emb1, emb2, emb3])

        query = [1.0, 0.0]  # Most similar to "east"
        results = index.search(query, k=2)

        assert len(results) == 2
        assert results[0].text == "east"
        assert results[1].text == "east-ish"

    def test_search_with_threshold(self):
        """Should filter by threshold."""
        index = EmbeddingIndex()

        emb1 = Embedding(vector=[1.0, 0.0], text="a", model="test")
        emb2 = Embedding(vector=[0.0, 1.0], text="b", model="test")
        index.add_batch([emb1, emb2])

        results = index.search([1.0, 0.0], k=10, threshold=0.9)

        assert len(results) == 1
        assert results[0].text == "a"

    def test_remove(self):
        """Should remove embeddings by text."""
        index = EmbeddingIndex()

        index.add(Embedding(vector=[0.1], text="remove_me", model="t"))
        index.add(Embedding(vector=[0.2], text="keep_me", model="t"))

        removed = index.remove("remove_me")
        assert removed == 1
        assert index.count == 1


class TestEmbeddingService:
    """Tests for EmbeddingService."""

    def test_embed_with_cache(self):
        """Should use cache."""
        provider = TestEmbeddingProvider()
        service = EmbeddingService(provider=provider)

        # First call - cache miss
        emb1 = service.embed("hello")
        assert service.stats["cache_hits"] == 0
        assert service.stats["api_calls"] == 1

        # Second call - cache hit
        emb2 = service.embed("hello")
        assert service.stats["cache_hits"] == 1
        assert service.stats["api_calls"] == 1

        assert emb1.vector == emb2.vector

    def test_embed_texts_batch(self):
        """Should batch embed texts."""
        provider = TestEmbeddingProvider()
        service = EmbeddingService(provider=provider)

        embeddings = service.embed_texts(["a", "b", "c"])

        assert len(embeddings) == 3
        assert embeddings[0].text == "a"

    def test_cache_hit_rate(self):
        """Should calculate hit rate."""
        provider = TestEmbeddingProvider()
        service = EmbeddingService(provider=provider)

        service.embed("a")
        service.embed("a")  # Hit
        service.embed("b")
        service.embed("b")  # Hit

        assert service.cache_hit_rate == 0.5


class TestChunkText:
    """Tests for chunk_text function."""

    def test_short_text(self):
        """Short text should not be chunked."""
        chunks = chunk_text("hello", chunk_size=100)
        assert len(chunks) == 1
        assert chunks[0] == "hello"

    def test_long_text(self):
        """Long text should be chunked."""
        text = "word " * 100  # 500 chars
        chunks = chunk_text(text, chunk_size=100, overlap=20)

        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
