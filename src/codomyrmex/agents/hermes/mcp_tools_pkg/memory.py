"""Hermes MCP tools — memory category."""
from __future__ import annotations

from typing import Any

from codomyrmex.agents.hermes.mcp_tools_pkg._client import _get_client
from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="hermes",
    description=(
        "Search the agentic memory (SQLite FTS5) for past conversational context. "
        "Use this when you need to recall past decisions or specific topics discussed previously."
    ),
)
def hermes_recall_memory(query: str, limit: int = 10) -> dict[str, Any]:
    """Search for past session text using FTS BM25 ranking.

    Args:
        query: Full-text search string (supports SQLite MATCH syntax).
        limit: Number of results to return (default 10).

    Returns:
        dict with status, and results list containing matched snippets.

    """
    try:
        from codomyrmex.agents.hermes.hermes_paths import resolve_hermes_session_db
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        db_path = resolve_hermes_session_db()

        with SQLiteSessionStore(db_path) as store:
            results = store.search_fts(query, limit)
            return {
                "status": "success",
                "count": len(results),
                "results": results,
            }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "results": []}

@mcp_tool(
    category="hermes",
    description="Search Hermes sessions by name substring.",
)
def hermes_session_search(query: str) -> dict[str, Any]:
    """Search sessions by name.

    Args:
        query: Substring to match against session names.

    Returns:
        dict with keys: status, sessions, count

    """
    try:
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        client = _get_client()
        with SQLiteSessionStore(client._session_db_path) as store:
            results = store.search_sessions(query)
            return {"status": "success", "sessions": results, "count": len(results)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description=(
        "Extract bi-directional [[Concept Link]] references from all Hermes sessions "
        "and return a lightweight knowledge graph of nodes and edges. "
        "Use this to see how topics connect across the agentic memory."
    ),
)
def hermes_build_memory_graph(
    min_link_count: int = 1,
) -> dict[str, Any]:
    """Build a concept-link graph from all Hermes session messages.

    Scans every stored session for ``[[WikiLink]]``-style references and
    constructs a directed graph where nodes are concept names and edges
    represent co-occurrence within the same session.

    Args:
        min_link_count: Minimum number of sessions a concept must appear in
            to be included as a node (default 1).

    Returns:
        dict with status, nodes (list of str), edges (list of {source, target, weight}),
        and session_count.
    """
    try:
        import re
        from collections import Counter, defaultdict

        from codomyrmex.agents.hermes.hermes_paths import resolve_hermes_session_db
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        db_path = resolve_hermes_session_db()

        WIKI_LINK_RE = re.compile(r"\[\[([^\[\]|#]+?)(?:[|#][^\]]+)?\]\]")

        concept_sessions: dict[str, set[str]] = defaultdict(set)
        edge_weights: Counter[tuple[str, str]] = Counter()

        with SQLiteSessionStore(db_path) as store:
            session_ids = store.list_sessions()
            for sid in session_ids:
                session = store.load(sid)
                if session is None:
                    continue
                full_text = " ".join(m.get("content", "") for m in session.messages)
                concepts_in_session = set(WIKI_LINK_RE.findall(full_text))
                for concept in concepts_in_session:
                    concept_sessions[concept].add(sid)
                # Directed edges: concept → all other concepts in same session
                for c1 in concepts_in_session:
                    for c2 in concepts_in_session:
                        if c1 != c2:
                            edge_weights[(c1, c2)] += 1

        # Filter to nodes that appear in enough sessions
        nodes = [
            c for c, sids in concept_sessions.items() if len(sids) >= min_link_count
        ]
        node_set = set(nodes)
        edges = [
            {"source": src, "target": tgt, "weight": w}
            for (src, tgt), w in edge_weights.items()
            if src in node_set and tgt in node_set
        ]

        return {
            "status": "success",
            "session_count": len(session_ids),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": sorted(nodes),
            "edges": sorted(edges, key=lambda e: -e["weight"]),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "nodes": [], "edges": []}

@mcp_tool(
    category="hermes",
    description=(
        "Extract a structured Knowledge Item (KI) from a Hermes session and persist it "
        "to the agentic knowledge memory. Use after complex multi-step sessions to "
        "crystallise reusable knowledge for future recall."
    ),
)
def hermes_extract_ki(
    session_id: str,
    title: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Persist a Knowledge Item derived from a Hermes session.

    Loads the session messages, concatenates the assistant turns into a body,
    and stores it via :class:`~codomyrmex.agentic_memory.memory.KnowledgeMemory`.

    Args:
        session_id: The Hermes session to extract from.
        title: Short title for the KI (auto-generated from session name if omitted).
        tags: Optional topic tags.

    Returns:
        dict with status, memory_id, title, and body_length.
    """
    try:
        from codomyrmex.agentic_memory.memory import KnowledgeMemory
        from codomyrmex.agents.hermes.hermes_paths import resolve_hermes_session_db
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        db_path = resolve_hermes_session_db()

        with SQLiteSessionStore(db_path) as store:
            session = store.load(session_id)

        if session is None:
            return {"status": "error", "message": f"Session '{session_id}' not found."}

        # Extract assistant outputs as the KI body
        body_parts = [
            m["content"]
            for m in session.messages
            if m.get("role") == "assistant" and m.get("content")
        ]
        body = "\n\n".join(body_parts) if body_parts else "(no assistant turns)"

        ki_title = title or (session.name or f"KI from session {session_id[:8]}")

        km = KnowledgeMemory()
        mem = km.store(
            title=ki_title,
            body=body,
            tags=tags or [],
            source_session_id=session_id,
        )

        return {
            "status": "success",
            "memory_id": mem.id,
            "title": ki_title,
            "body_length": len(body),
            "tags": tags or [],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

@mcp_tool(
    category="hermes",
    description=(
        "Search stored Knowledge Items (KIs) by topic. Returns ranked results from "
        "the agentic semantic memory. Use before beginning complex tasks to check if "
        "the relevant knowledge has already been codified."
    ),
)
def hermes_search_knowledge_items(
    topic: str,
    limit: int = 5,
) -> dict[str, Any]:
    """Retrieve ranked Knowledge Items relevant to *topic*.

    Uses token-overlap relevance scoring across all SEMANTIC memories.

    Args:
        topic: Natural language search string.
        limit: Maximum number of results to return.

    Returns:
        dict with status, count, and results list containing title, body snippet, score.
    """
    try:
        from codomyrmex.agentic_memory.memory import KnowledgeMemory

        km = KnowledgeMemory()
        results = km.recall(topic, k=limit)

        items = []
        for r in results:
            meta = r.memory.metadata or {}
            items.append(
                {
                    "memory_id": r.memory.id,
                    "title": meta.get("title", "(untitled)"),
                    "snippet": r.memory.content[:200],
                    "tags": meta.get("tags", []),
                    "source_session_id": meta.get("source_session_id", ""),
                    "relevance": round(r.relevance_score, 4),
                    "combined_score": round(r.combined_score, 4),
                }
            )

        return {
            "status": "success",
            "topic": topic,
            "count": len(items),
            "results": items,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "results": []}

@mcp_tool(
    category="hermes",
    description=(
        "Merge near-duplicate Knowledge Items in the agentic memory to keep the "
        "knowledge base clean and non-redundant. Items above the similarity threshold "
        "are folded into their older counterpart as dated Update sections."
    ),
)
def hermes_deduplicate_ki(
    threshold: float = 0.85,
) -> dict[str, Any]:
    """Deduplicate Knowledge Items by merging similar entries.

    Computes token-overlap similarity between all SEMANTIC memories.
    Items with similarity ≥ *threshold* relative to an existing older item
    are merged into it (body appended as ``## Update``) and deleted.

    Args:
        threshold: Similarity threshold 0.0–1.0 (default 0.85).

    Returns:
        dict with status, merged_count, and message.
    """
    try:
        from codomyrmex.agentic_memory.memory import KnowledgeMemory

        km = KnowledgeMemory()
        merged = km.merge_duplicates(threshold=threshold)

        return {
            "status": "success",
            "merged_count": merged,
            "threshold": threshold,
            "message": f"Merged {merged} duplicate Knowledge Item(s) at threshold {threshold}.",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
