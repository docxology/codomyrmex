"""Tests for ChromaVectorStore."""

import uuid

import pytest

from codomyrmex.vector_store.chroma import ChromaVectorStore


@pytest.fixture
def chroma_store():
    # EphemeralClient used automatically when no persist_directory is provided
    store = ChromaVectorStore(collection_name=f"test_collection_{uuid.uuid4().hex}")
    yield store
    store.clear()


class TestChromaVectorStore:
    def test_add_and_get(self, chroma_store):
        chroma_store.add("1", [0.1, 0.2, 0.3], {"type": "test"})
        entry = chroma_store.get("1")
        
        assert entry is not None
        assert entry.id == "1"
        assert len(entry.embedding) == 3
        # Float comparisons with precision issues in Chroma
        assert abs(entry.embedding[0] - 0.1) < 1e-5
        assert entry.metadata == {"type": "test"}

    def test_get_nonexistent(self, chroma_store):
        assert chroma_store.get("invalid") is None

    def test_delete(self, chroma_store):
        chroma_store.add("1", [0.1, 0.2, 0.3])
        assert chroma_store.delete("1") is True
        assert chroma_store.get("1") is None
        assert chroma_store.delete("1") is False

    def test_search(self, chroma_store):
        chroma_store.add("1", [1.0, 0.0, 0.0], {"name": "x-axis"})
        chroma_store.add("2", [0.0, 1.0, 0.0], {"name": "y-axis"})
        
        # Searching for something close to x-axis
        results = chroma_store.search([0.9, 0.1, 0.0], k=1)
        
        assert len(results) == 1
        assert results[0].id == "1"
        assert results[0].metadata["name"] == "x-axis"
        assert results[0].score > 0.0

    def test_search_with_filter(self, chroma_store):
        chroma_store.add("1", [1.0, 0.0], {"color": "red"})
        chroma_store.add("2", [1.0, 0.0], {"color": "blue"})
        
        results = chroma_store.search(
            [1.0, 0.0], 
            k=10, 
            filter_fn=lambda m: m.get("color") == "blue"
        )
        
        assert len(results) == 1
        assert results[0].id == "2"

    def test_count_and_clear(self, chroma_store):
        assert chroma_store.count() == 0
        chroma_store.add("1", [1.0])
        chroma_store.add("2", [0.5])
        assert chroma_store.count() == 2
        
        chroma_store.clear()
        assert chroma_store.count() == 0
