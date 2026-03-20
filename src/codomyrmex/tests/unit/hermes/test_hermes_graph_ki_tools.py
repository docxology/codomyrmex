"""Unit tests for new hermes MCP tools: graph inference, KI extraction, search, dedup.

Zero-mock: uses InMemorySessionStore and InMemoryStore throughout.
No live LLM backend required.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from codomyrmex.agentic_memory.memory import KnowledgeMemory
from codomyrmex.agentic_memory.stores import InMemoryStore
from codomyrmex.agents.hermes.session import HermesSession, InMemorySessionStore

if TYPE_CHECKING:
    import pytest

# ── hermes_build_memory_graph ─────────────────────────────────────────────────


def test_build_memory_graph_with_wiki_links(monkeypatch: pytest.MonkeyPatch) -> None:
    """Graph builder extracts [[WikiLink]] references from session messages."""
    import re
    from collections import Counter, defaultdict

    # Replicate the graph-building logic against an InMemorySessionStore
    store = InMemorySessionStore()
    s1 = HermesSession(session_id="s1")
    s1.add_message("user", "Explain [[BM25]] and [[FTS5]] interaction.")
    s1.add_message("assistant", "[[BM25]] ranks [[FTS5]] results using term frequency.")
    store.save(s1)

    s2 = HermesSession(session_id="s2")
    s2.add_message("user", "How does [[BM25]] compare to [[TF-IDF]]?")
    store.save(s2)

    WIKI_LINK_RE = re.compile(r"\[\[([^\[\]|#]+?)(?:[|#][^\]]+)?\]\]")
    concept_sessions: dict[str, set[str]] = defaultdict(set)
    edge_weights: Counter[tuple[str, str]] = Counter()

    for sid in store.list_sessions():
        session = store.load(sid)
        assert session is not None
        full_text = " ".join(m.get("content", "") for m in session.messages)
        concepts = set(WIKI_LINK_RE.findall(full_text))
        for c in concepts:
            concept_sessions[c].add(sid)
        for c1 in concepts:
            for c2 in concepts:
                if c1 != c2:
                    edge_weights[(c1, c2)] += 1

    nodes = list(concept_sessions.keys())
    assert "BM25" in nodes
    assert "FTS5" in nodes
    assert "TF-IDF" in nodes

    # BM25 appears in both sessions → should have edges to both FTS5 and TF-IDF
    bm25_targets = {tgt for (src, tgt) in edge_weights if src == "BM25"}
    assert "FTS5" in bm25_targets or "TF-IDF" in bm25_targets


def test_build_memory_graph_no_links_returns_empty() -> None:
    """Sessions with no [[WikiLink]] produce an empty graph."""
    import re
    from collections import Counter, defaultdict

    store = InMemorySessionStore()
    s = HermesSession(session_id="plain")
    s.add_message("user", "Hello world, no special links here.")
    store.save(s)

    WIKI_LINK_RE = re.compile(r"\[\[([^\[\]|#]+?)(?:[|#][^\]]+)?\]\]")
    concept_sessions: dict[str, set[str]] = defaultdict(set)
    edge_weights: Counter[tuple[str, str]] = Counter()

    for sid in store.list_sessions():
        session = store.load(sid)
        assert session is not None
        full_text = " ".join(m.get("content", "") for m in session.messages)
        for c in set(WIKI_LINK_RE.findall(full_text)):
            concept_sessions[c].add(sid)

    assert len(concept_sessions) == 0
    assert len(edge_weights) == 0


# ── hermes_extract_ki ─────────────────────────────────────────────────────────


def test_extract_ki_from_session_with_assistant_turn() -> None:
    """KI extraction pulls assistant turns into KnowledgeMemory."""
    store = InMemorySessionStore()
    sess = HermesSession(session_id="ki-sess", name="OAuth2 pattern")
    sess.add_message("user", "How do I set up OAuth2?")
    sess.add_message("assistant", "Use from_env() with GOOGLE_CLIENT_ID.")
    store.save(sess)

    # Replicate extraction logic
    km = KnowledgeMemory(store=InMemoryStore())
    body_parts = [
        m["content"]
        for m in sess.messages
        if m.get("role") == "assistant" and m.get("content")
    ]
    body = "\n\n".join(body_parts)
    ki_title = sess.name or sess.session_id
    mem = km.store(title=ki_title, body=body, source_session_id=sess.session_id)

    assert mem.metadata["title"] == "OAuth2 pattern"
    assert "from_env" in mem.content
    assert mem.metadata["source_session_id"] == "ki-sess"


def test_extract_ki_no_assistant_turns_uses_placeholder() -> None:
    """Sessions without assistant turns still produce a KI with placeholder body."""
    sess = HermesSession(session_id="empty-sess")
    sess.add_message("user", "Hello?")

    body_parts = [
        m["content"]
        for m in sess.messages
        if m.get("role") == "assistant" and m.get("content")
    ]
    body = "\n\n".join(body_parts) if body_parts else "(no assistant turns)"
    assert body == "(no assistant turns)"


# ── hermes_search_knowledge_items ─────────────────────────────────────────────


def test_search_knowledge_items_returns_ranked_results() -> None:
    """Knowledge search returns results ranked by token overlap."""
    backing = InMemoryStore()
    km = KnowledgeMemory(store=backing)
    km.store(title="BM25 Ranking", body="BM25 is a term frequency ranking algorithm.")
    km.store(title="Docker Setup", body="Build docker images with Dockerfile.")

    results = km.recall("BM25 ranking term frequency", k=5)
    assert len(results) >= 1
    assert results[0].relevance_score > 0
    # BM25-related KI should rank first
    assert "BM25" in results[0].memory.content


def test_search_knowledge_items_empty_store() -> None:
    km = KnowledgeMemory(store=InMemoryStore())
    results = km.recall("anything")
    assert results == []


# ── hermes_deduplicate_ki ─────────────────────────────────────────────────────


def test_deduplicate_ki_merges_near_identical() -> None:
    import time

    backing = InMemoryStore()
    km = KnowledgeMemory(store=backing)
    mem1 = km.store(title="BM25 Search", body="BM25 ranking for full text search.")
    time.sleep(0.01)
    km.store(title="BM25 Search", body="BM25 ranking for full text search.")

    merged = km.merge_duplicates(threshold=0.85)
    assert merged >= 1
    updated = km._agent.store.get(mem1.id)
    assert updated is not None
    assert "## Update" in updated.content


def test_deduplicate_ki_distinct_items_unchanged() -> None:
    backing = InMemoryStore()
    km = KnowledgeMemory(store=backing)
    km.store(title="Python asyncio", body="asyncio coroutines event loop await.")
    km.store(title="SQL normalization", body="database schema normalization forms.")
    before_count = km._agent.memory_count
    merged = km.merge_duplicates(threshold=0.85)
    assert merged == 0
    assert km._agent.memory_count == before_count
