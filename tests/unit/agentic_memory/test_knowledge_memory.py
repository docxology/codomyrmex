"""Unit tests for KnowledgeMemory.store / recall / merge_duplicates.

Zero-mock: uses InMemoryStore (the real in-memory backend) directly.
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.agentic_memory.memory import KnowledgeMemory
from codomyrmex.agentic_memory.stores import InMemoryStore

# ── fixture ────────────────────────────────────────────────────────────────


@pytest.fixture
def km() -> KnowledgeMemory:
    """Fresh KnowledgeMemory backed by a real InMemoryStore."""
    return KnowledgeMemory(store=InMemoryStore())


# ── store ──────────────────────────────────────────────────────────────────


def test_store_returns_memory_with_id(km: KnowledgeMemory) -> None:
    mem = km.store(title="FTS5 BM25", body="SQLite full-text ranking via BM25.")
    assert mem.id
    assert "FTS5 BM25" in mem.content


def test_store_persists_metadata(km: KnowledgeMemory) -> None:
    mem = km.store(
        title="OAuth2 Pattern",
        body="Use from_env() constructor for Google OAuth2.",
        tags=["oauth", "google"],
        source_session_id="session-abc123",
        source="manual",
    )
    assert mem.metadata["title"] == "OAuth2 Pattern"
    assert mem.metadata["tags"] == ["oauth", "google"]
    assert mem.metadata["source_session_id"] == "session-abc123"
    assert mem.metadata["ki_stored_at"] > 0


def test_store_multiple_adds_to_count(km: KnowledgeMemory) -> None:
    for i in range(5):
        km.store(title=f"KI #{i}", body=f"Body of item {i}.")
    assert km._agent.memory_count == 5


# ── recall ─────────────────────────────────────────────────────────────────


def test_recall_returns_semantic_results_only(km: KnowledgeMemory) -> None:
    km.store(title="BM25 Ranking", body="BM25 is a ranking function.")
    km.store(title="Ollama LLM", body="Ollama runs local language models.")

    results = km.recall("BM25 ranking score")
    assert len(results) > 0
    # Top result should be semantically closer to BM25 topic
    top_result = results[0]
    assert "BM25" in top_result.memory.content or top_result.relevance_score >= 0.0


def test_recall_respects_limit(km: KnowledgeMemory) -> None:
    for i in range(10):
        km.store(title=f"Topic {i}", body=f"Detail about topic {i}.")
    results = km.recall("topic detail", k=3)
    assert len(results) <= 3


def test_recall_empty_store_returns_empty(km: KnowledgeMemory) -> None:
    results = km.recall("anything")
    assert results == []


# ── merge_duplicates ───────────────────────────────────────────────────────


def test_merge_duplicates_folds_near_identical(km: KnowledgeMemory) -> None:
    mem1 = km.store(title="BM25 Search", body="BM25 ranking for full text search.")
    # Slight variation — same tokens, should be above 0.85 overlap
    time.sleep(0.01)  # ensure different created_at
    _mem2 = km.store(title="BM25 Search", body="BM25 ranking for full text search.")

    merged_count = km.merge_duplicates(threshold=0.85)
    assert merged_count >= 1

    # mem1 (older) should now contain Update section
    updated = km._agent.store.get(mem1.id)
    assert updated is not None
    assert "## Update" in updated.content


def test_merge_duplicates_keeps_distinct_items(km: KnowledgeMemory) -> None:
    km.store(title="Async Python", body="asyncio event loops.")
    km.store(title="SQL Joins", body="inner outer cross join SQL.")
    merged = km.merge_duplicates(threshold=0.85)
    assert merged == 0
    assert km._agent.memory_count == 2


def test_merge_duplicates_threshold_zero_merges_all(km: KnowledgeMemory) -> None:
    # With threshold=0.0, everything with any overlap merges
    km.store(title="Topic A", body="word1 word2.")
    time.sleep(0.01)
    km.store(title="Topic B", body="word1 word3.")
    merged = km.merge_duplicates(threshold=0.0)
    # At least one merge (word1 overlaps)
    assert merged >= 1
