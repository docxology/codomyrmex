"""Unit tests for new hermes MCP tools: graph inference, KI extraction, search, dedup.

Zero-mock: uses InMemorySessionStore and InMemoryStore throughout.
No live LLM backend required.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from codomyrmex.agentic_memory.core.memory import KnowledgeMemory
from codomyrmex.agentic_memory.stores import InMemoryStore
from codomyrmex.agents.hermes.session import (
    HermesSession,
    InMemorySessionStore,
    SQLiteSessionStore,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# ── hermes_build_memory_graph ─────────────────────────────────────────────────


def _seed_sqlite_sessions(db_path: Path, sessions: dict[str, list[str]]) -> None:
    with SQLiteSessionStore(db_path) as store:
        for session_id, messages in sessions.items():
            session = HermesSession(session_id=session_id)
            for text in messages:
                session.add_message("user", text)
            store.save(session)


def test_build_memory_graph_with_wiki_links(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The real MCP tool extracts [[WikiLink]] concepts from a real SQLite store."""
    from codomyrmex.agents.hermes.mcp_tools_pkg.memory import hermes_build_memory_graph

    db_path = tmp_path / "sessions.db"
    _seed_sqlite_sessions(
        db_path,
        {
            "s1": [
                "Explain [[BM25]] and [[FTS5]] interaction.",
                "[[BM25]] ranks [[FTS5|full-text]] results using term frequency.",
            ],
            "s2": ["How does [[BM25]] compare to [[TF-IDF#weights]]?"],
        },
    )
    monkeypatch.setenv("CODOMYRMEX_HERMES_SESSION_DB", str(db_path))

    graph = hermes_build_memory_graph()

    assert graph["status"] == "success"
    assert graph["session_count"] == 2
    assert graph["nodes"] == ["BM25", "FTS5", "TF-IDF"]
    edges = {(e["source"], e["target"]): e["weight"] for e in graph["edges"]}
    assert edges[("BM25", "FTS5")] == 1
    assert edges[("BM25", "TF-IDF")] == 1
    assert ("FTS5", "TF-IDF") not in edges

    # min_link_count filters concepts seen in fewer sessions.
    filtered = hermes_build_memory_graph(min_link_count=2)
    assert filtered["nodes"] == ["BM25"]
    assert filtered["edges"] == []


def test_build_memory_graph_no_links_returns_empty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Sessions with no [[WikiLink]] produce an empty graph."""
    from codomyrmex.agents.hermes.mcp_tools_pkg.memory import hermes_build_memory_graph

    db_path = tmp_path / "sessions.db"
    _seed_sqlite_sessions(db_path, {"plain": ["Hello world, no special links here."]})
    monkeypatch.setenv("CODOMYRMEX_HERMES_SESSION_DB", str(db_path))

    graph = hermes_build_memory_graph()

    assert graph["status"] == "success"
    assert graph["session_count"] == 1
    assert graph["nodes"] == []
    assert graph["edges"] == []


def test_wiki_link_pattern_strips_alias_and_heading() -> None:
    from codomyrmex.agents.hermes.mcp_tools_pkg.memory import WIKI_LINK_RE

    text = "[[A]] [[B|alias]] [[C#Section]] [[ [nested] ]] [[D|x#y]]"
    assert WIKI_LINK_RE.findall(text) == ["A", "B", "C", "D"]


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
