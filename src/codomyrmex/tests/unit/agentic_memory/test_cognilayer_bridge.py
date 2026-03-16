"""Tests for agentic_memory/cognilayer_bridge.py — uses a temp SQLite database.

All tests create a real temporary database file so there are zero mocks.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from codomyrmex.agentic_memory.cognilayer_bridge import (
    _get_db_connection,
    consolidate_memories,
    get_memory_stats,
    recall_memory,
    store_memory,
)
from codomyrmex.agentic_memory.models import MemoryImportance


@pytest.fixture()
def tmp_db(tmp_path: Path) -> Path:
    """Create a temporary SQLite database with a memories table."""
    db_path = tmp_path / "memory.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """CREATE TABLE memories (
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
    conn.commit()
    conn.close()
    return db_path


def _patch_db(db_path: Path):
    """Helper to patch COGNILAYER_DB and COGNILAYER_HOME in the module."""
    return patch.multiple(
        "codomyrmex.agentic_memory.cognilayer_bridge",
        COGNILAYER_DB=db_path,
        COGNILAYER_HOME=db_path.parent,
    )


class TestGetDbConnection:
    """Tests for _get_db_connection."""

    def test_raises_if_db_missing(self, tmp_path: Path) -> None:
        """FileNotFoundError raised when database does not exist."""
        missing = tmp_path / "no_db_here.db"
        with patch(
            "codomyrmex.agentic_memory.cognilayer_bridge.COGNILAYER_DB", missing
        ):
            with pytest.raises(FileNotFoundError, match="not found"):
                _get_db_connection()

    def test_returns_connection_when_db_exists(self, tmp_db: Path) -> None:
        """Returns a valid sqlite3 connection for an existing database."""
        with _patch_db(tmp_db):
            conn = _get_db_connection()
            try:
                assert conn.row_factory == sqlite3.Row
                # Verify we can query the memories table
                count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
                assert count == 0
            finally:
                conn.close()


class TestStoreMemory:
    """Tests for store_memory."""

    def test_store_basic(self, tmp_db: Path) -> None:
        """A basic memory entry is stored and returned with an id."""
        with _patch_db(tmp_db):
            result = store_memory(
                "Test content for storage",
                key="test-key",
                tags=["tag1", "tag2"],
            )
        assert result["key"] == "test-key"
        assert result["id"] is not None
        assert result["tags"] == ["tag1", "tag2"]
        assert "Test content" in result["content"]

    def test_store_truncates_long_content(self, tmp_db: Path) -> None:
        """Content longer than 100 chars is truncated in the returned dict."""
        long_content = "x" * 200
        with _patch_db(tmp_db):
            result = store_memory(long_content, key="long")
        assert result["content"].endswith("...")
        assert len(result["content"]) == 103  # 100 + "..."

    def test_store_with_metadata(self, tmp_db: Path) -> None:
        """Metadata dict is serialized to JSON."""
        with _patch_db(tmp_db):
            result = store_memory(
                "Meta test",
                key="meta-key",
                metadata={"source": "test", "count": 42},
            )
        assert result["id"] is not None

        # Verify it's actually in the DB
        with _patch_db(tmp_db):
            conn = _get_db_connection()
            row = conn.execute(
                "SELECT metadata FROM memories WHERE key = ?", ("meta-key",)
            ).fetchone()
            conn.close()
        assert '"source": "test"' in row["metadata"]

    def test_store_with_different_importance_levels(self, tmp_db: Path) -> None:
        """All importance levels are stored correctly."""
        for imp in MemoryImportance:
            with _patch_db(tmp_db):
                result = store_memory(
                    f"Content for {imp.name}",
                    key=f"key-{imp.name}",
                    importance=imp,
                )
            assert result["id"] is not None


class TestRecallMemory:
    """Tests for recall_memory."""

    def _seed(self, db_path: Path) -> None:
        """Insert test data into the memories table."""
        conn = sqlite3.connect(str(db_path))
        entries = [
            ("k1", "Python is a programming language", "lang,code"),
            ("k2", "JavaScript runs in browsers", "lang,web"),
            ("k3", "Docker containers are isolated environments", "devops"),
            ("k4", "Python decorators modify function behavior", "lang,code"),
        ]
        for key, content, tags in entries:
            conn.execute(
                """INSERT INTO memories (key, content, tags, importance, type, metadata, created_at, updated_at)
                   VALUES (?, ?, ?, 'medium', 'knowledge', '{}', '2025-01-01T00:00:00', '2025-01-01T00:00:00')""",
                (key, content, tags),
            )
        conn.commit()
        conn.close()

    def test_recall_returns_results(self, tmp_db: Path) -> None:
        """LIKE-based fallback search returns matching memories."""
        self._seed(tmp_db)
        with _patch_db(tmp_db):
            results = recall_memory("Python", top_k=10)
        assert len(results) >= 2
        contents = [r["content"] for r in results]
        assert any("programming language" in c for c in contents)

    def test_recall_respects_top_k(self, tmp_db: Path) -> None:
        """top_k limits the number of returned results."""
        self._seed(tmp_db)
        with _patch_db(tmp_db):
            results = recall_memory("Python", top_k=1)
        assert len(results) == 1

    def test_recall_with_tag_filter(self, tmp_db: Path) -> None:
        """Tag filtering narrows results to matching tags."""
        self._seed(tmp_db)
        with _patch_db(tmp_db):
            results = recall_memory("Python", top_k=10, tags=["web"])
        # Only JavaScript has 'web' tag, Python entries don't
        assert len(results) == 0

        with _patch_db(tmp_db):
            results = recall_memory("Python", top_k=10, tags=["code"])
        assert len(results) >= 1

    def test_recall_empty_query_returns_all(self, tmp_db: Path) -> None:
        """Empty query with LIKE fallback returns limited results."""
        self._seed(tmp_db)
        with _patch_db(tmp_db):
            results = recall_memory("", top_k=2)
        assert len(results) <= 2


class TestConsolidateMemories:
    """Tests for consolidate_memories."""

    def test_removes_duplicates(self, tmp_path: Path) -> None:
        """Duplicate keys are deduplicated, keeping the latest row.

        Uses a database without the UNIQUE constraint to allow inserting
        duplicate key rows (simulating data corruption or legacy imports).
        """
        # Create a DB without UNIQUE constraint on key
        db_path = tmp_path / "dup_memory.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute(
            """CREATE TABLE memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                content TEXT NOT NULL,
                tags TEXT DEFAULT '',
                importance TEXT DEFAULT 'medium',
                type TEXT DEFAULT 'knowledge',
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )"""
        )
        for i in range(3):
            conn.execute(
                """INSERT INTO memories (key, content, tags, importance, type, metadata, created_at, updated_at)
                   VALUES (?, ?, '', 'medium', 'knowledge', '{}', ?, ?)""",
                ("dup-key", f"Version {i}", f"2025-01-0{i+1}T00:00:00", f"2025-01-0{i+1}T00:00:00"),
            )
        conn.commit()
        conn.close()

        with patch.multiple(
            "codomyrmex.agentic_memory.cognilayer_bridge",
            COGNILAYER_DB=db_path,
            COGNILAYER_HOME=db_path.parent,
        ):
            result = consolidate_memories()
        assert result["before"] == 3
        assert result["after"] == 1
        assert result["removed"] == 2

    def test_no_duplicates(self, tmp_db: Path) -> None:
        """When no duplicates exist, nothing is removed."""
        conn = sqlite3.connect(str(tmp_db))
        for i in range(3):
            conn.execute(
                """INSERT INTO memories (key, content, tags, importance, type, metadata, created_at, updated_at)
                   VALUES (?, ?, '', 'medium', 'knowledge', '{}', '2025-01-01T00:00:00', '2025-01-01T00:00:00')""",
                (f"key-{i}", f"Content {i}"),
            )
        conn.commit()
        conn.close()

        with _patch_db(tmp_db):
            result = consolidate_memories()
        assert result["before"] == 3
        assert result["after"] == 3
        assert result["removed"] == 0


class TestGetMemoryStats:
    """Tests for get_memory_stats."""

    def test_returns_stats_when_db_exists(self, tmp_db: Path) -> None:
        """Stats include table list, db path, and memory count."""
        conn = sqlite3.connect(str(tmp_db))
        conn.execute(
            """INSERT INTO memories (key, content, tags, importance, type, metadata, created_at, updated_at)
               VALUES ('k1', 'test', '', 'medium', 'knowledge', '{}', '2025-01-01T00:00:00', '2025-01-01T00:00:00')"""
        )
        conn.commit()
        conn.close()

        with _patch_db(tmp_db):
            stats = get_memory_stats()
        assert stats["installed"] is True
        assert "memories" in stats["tables"]
        assert stats["total_memories"] == 1
        assert stats["db_size_bytes"] > 0

    def test_returns_not_installed_when_db_missing(self, tmp_path: Path) -> None:
        """Returns installed=False when the database file does not exist."""
        missing = tmp_path / "nope.db"
        with patch(
            "codomyrmex.agentic_memory.cognilayer_bridge.COGNILAYER_DB", missing
        ):
            stats = get_memory_stats()
        assert stats["installed"] is False
        assert "not found" in stats.get("error", "").lower()
