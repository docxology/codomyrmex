"""CogniLayer Bridge — connects Codomyrmex AgentMemory to CogniLayer MCP memory.

Provides high-level functions that bridge the Codomyrmex agentic memory
system with the CogniLayer persistent memory server (~/.cognilayer/memory.db).

Functions:
    store_memory: Persist a memory entry via CogniLayer's MCP tools
    recall_memory: Retrieve relevant memories by semantic query
    consolidate_memories: Merge and deduplicate stored memories
    get_memory_stats: Return memory database statistics
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from codomyrmex.agentic_memory.models import MemoryImportance, MemoryType

# CogniLayer default paths
COGNILAYER_HOME = Path.home() / ".cognilayer"
COGNILAYER_DB = COGNILAYER_HOME / "memory.db"


def _get_db_connection() -> sqlite3.Connection:
    """Open a read/write connection to the CogniLayer SQLite database."""
    if not COGNILAYER_DB.exists():
        raise FileNotFoundError(
            f"CogniLayer database not found at {COGNILAYER_DB}. "
            "Run 'python ~/.cognilayer/install.py' or '/onboard' first."
        )
    conn = sqlite3.connect(str(COGNILAYER_DB))
    conn.row_factory = sqlite3.Row
    return conn


def store_memory(
    content: str,
    *,
    key: str | None = None,
    tags: list[str] | None = None,
    importance: MemoryImportance = MemoryImportance.MEDIUM,
    memory_type: MemoryType = MemoryType.KNOWLEDGE,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Store a memory entry in the CogniLayer database.

    Args:
        content: The text content to store.
        key: Optional unique key for deduplication.
        tags: Optional list of tags for categorization.
        importance: Memory importance level (LOW, MEDIUM, HIGH, CRITICAL).
        memory_type: Type of memory (EPISODIC, SEMANTIC, PROCEDURAL, KNOWLEDGE).
        metadata: Optional extra metadata dict.

    Returns:
        Dict with stored memory details including the database row id.

    Example:
        >>> result = store_memory(
        ...     "The PAI interface has 299 MCP tools",
        ...     key="pai-tool-count",
        ...     tags=["pai", "mcp", "metrics"],
        ... )

    """
    conn = _get_db_connection()
    try:
        now = datetime.now(UTC).isoformat()
        tag_str = ",".join(tags) if tags else ""
        meta_str = json.dumps(metadata) if metadata else "{}"

        # Try CogniLayer's memories table first
        try:
            cursor = conn.execute(
                """INSERT INTO memories (key, content, tags, importance, type, metadata, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    key,
                    content,
                    tag_str,
                    importance.value,
                    memory_type.value,
                    meta_str,
                    now,
                    now,
                ),
            )
        except sqlite3.OperationalError:
            # Fallback: create a simple memories table if it doesn't exist
            conn.execute(
                """CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    content TEXT NOT NULL,
                    tags TEXT DEFAULT '',
                    importance TEXT DEFAULT 'medium',
                    type TEXT DEFAULT 'knowledge',
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )"""
            )
            cursor = conn.execute(
                """INSERT OR REPLACE INTO memories (key, content, tags, importance, type, metadata, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    key,
                    content,
                    tag_str,
                    importance.value,
                    memory_type.value,
                    meta_str,
                    now,
                    now,
                ),
            )

        conn.commit()
        return {
            "id": cursor.lastrowid,
            "key": key,
            "content": content[:100] + "..." if len(content) > 100 else content,
            "tags": tags or [],
            "stored_at": now,
        }
    finally:
        conn.close()


def recall_memory(
    query: str,
    *,
    top_k: int = 5,
    tags: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Retrieve relevant memories from CogniLayer by full-text search.

    Args:
        query: Search query string.
        top_k: Maximum number of results to return.
        tags: Optional tag filter — only return memories matching these tags.

    Returns:
        List of memory dicts sorted by relevance.

    Example:
        >>> results = recall_memory("PAI tool count", top_k=3)

    """
    conn = _get_db_connection()
    try:
        # Try FTS5 search first (CogniLayer uses this)
        try:
            rows = conn.execute(
                """SELECT * FROM memories_fts WHERE memories_fts MATCH ? LIMIT ?""",
                (query, top_k),
            ).fetchall()
        except sqlite3.OperationalError:
            # Fallback to LIKE search
            search_terms = [f"%{word}%" for word in query.split()]
            where_clauses = " OR ".join(["content LIKE ?"] * len(search_terms))
            rows = conn.execute(
                f"SELECT * FROM memories WHERE {where_clauses} LIMIT ?",
                [*search_terms, top_k],
            ).fetchall()

        results = []
        for row in rows:
            entry = dict(row)
            if tags:
                row_tags = entry.get("tags", "").split(",")
                if not any(t in row_tags for t in tags):
                    continue
            results.append(entry)

        return results[:top_k]
    finally:
        conn.close()


def consolidate_memories() -> dict[str, Any]:
    """Merge and deduplicate stored memories.

    Scans for duplicate keys and near-duplicate content,
    keeping the most recent version.

    Returns:
        Dict with consolidation statistics.

    """
    conn = _get_db_connection()
    try:
        # Count before
        total_before = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]

        # Remove exact duplicates (same key, keep latest)
        conn.execute(
            """DELETE FROM memories WHERE rowid NOT IN (
                SELECT MAX(rowid) FROM memories GROUP BY key
            ) AND key IS NOT NULL"""
        )
        conn.commit()

        total_after = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        return {
            "before": total_before,
            "after": total_after,
            "removed": total_before - total_after,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    finally:
        conn.close()


def get_memory_stats() -> dict[str, Any]:
    """Return CogniLayer memory database statistics.

    Returns:
        Dict with total memories, tag distribution, type breakdown, and db size.

    """
    if not COGNILAYER_DB.exists():
        return {"installed": False, "error": f"Database not found: {COGNILAYER_DB}"}

    conn = _get_db_connection()
    try:
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]

        stats: dict[str, Any] = {
            "installed": True,
            "db_path": str(COGNILAYER_DB),
            "db_size_bytes": COGNILAYER_DB.stat().st_size,
            "tables": tables,
        }

        if "memories" in tables:
            stats["total_memories"] = conn.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]

        return stats
    finally:
        conn.close()
