"""Tests for agents.hermes.session module.

Covers HermesSession, InMemorySessionStore, and SQLiteSessionStore.
"""

from __future__ import annotations

import gzip
import json
import os
import time
from pathlib import Path

import pytest

from codomyrmex.agents.hermes.session import (
    HermesSession,
    InMemorySessionStore,
    SQLiteSessionStore,
)


# ---------------------------------------------------------------------------
# HermesSession dataclass
# ---------------------------------------------------------------------------


class TestHermesSession:
    """Tests for the HermesSession dataclass."""

    def test_default_creation(self):
        s = HermesSession()
        assert len(s.session_id) == 12
        assert s.messages == []
        assert s.metadata == {}
        assert s.name is None
        assert s.parent_session_id is None

    def test_custom_session_id(self):
        s = HermesSession(session_id="abc123")
        assert s.session_id == "abc123"

    def test_add_message(self):
        s = HermesSession()
        before = s.updated_at
        s.add_message("user", "hello")
        assert len(s.messages) == 1
        assert s.messages[0] == {"role": "user", "content": "hello"}
        assert s.updated_at >= before

    def test_message_count(self):
        s = HermesSession()
        assert s.message_count == 0
        s.add_message("user", "hi")
        s.add_message("assistant", "hey")
        assert s.message_count == 2

    def test_last_message_empty(self):
        s = HermesSession()
        assert s.last_message is None

    def test_last_message_present(self):
        s = HermesSession()
        s.add_message("user", "first")
        s.add_message("assistant", "second")
        assert s.last_message == {"role": "assistant", "content": "second"}

    def test_fork_inherits_messages(self):
        parent = HermesSession(session_id="parent-1", name="original")
        parent.add_message("user", "hello")
        parent.metadata["key"] = "value"

        child = parent.fork(new_name="child-1")

        assert child.parent_session_id == "parent-1"
        assert child.name == "child-1"
        assert child.messages == parent.messages
        assert child.metadata["forked_from"] == "parent-1"
        assert child.metadata["key"] == "value"
        assert child.session_id != parent.session_id

    def test_fork_default_name(self):
        parent = HermesSession(session_id="p1")
        child = parent.fork()
        assert child.name is None
        assert child.parent_session_id == "p1"


# ---------------------------------------------------------------------------
# InMemorySessionStore
# ---------------------------------------------------------------------------


class TestInMemorySessionStore:
    """Tests for InMemorySessionStore."""

    def test_save_and_load(self):
        store = InMemorySessionStore()
        s = HermesSession(session_id="s1")
        store.save(s)
        loaded = store.load("s1")
        assert loaded is not None
        assert loaded.session_id == "s1"

    def test_load_missing(self):
        store = InMemorySessionStore()
        assert store.load("nonexistent") is None

    def test_list_sessions(self):
        store = InMemorySessionStore()
        store.save(HermesSession(session_id="a"))
        store.save(HermesSession(session_id="b"))
        ids = store.list_sessions()
        assert set(ids) == {"a", "b"}

    def test_delete_existing(self):
        store = InMemorySessionStore()
        store.save(HermesSession(session_id="x"))
        assert store.delete("x") is True
        assert store.load("x") is None

    def test_delete_missing(self):
        store = InMemorySessionStore()
        assert store.delete("nope") is False

    def test_overwrite_save(self):
        store = InMemorySessionStore()
        s1 = HermesSession(session_id="dup", name="first")
        s2 = HermesSession(session_id="dup", name="second")
        store.save(s1)
        store.save(s2)
        loaded = store.load("dup")
        assert loaded.name == "second"


# ---------------------------------------------------------------------------
# SQLiteSessionStore
# ---------------------------------------------------------------------------


class TestSQLiteSessionStore:
    """Tests for SQLiteSessionStore (in-memory DB)."""

    @pytest.fixture()
    def store(self):
        """Provide an in-memory SQLiteSessionStore."""
        with SQLiteSessionStore(":memory:") as s:
            yield s

    def test_save_and_load(self, store):
        s = HermesSession(session_id="db-1", name="test-session")
        s.add_message("user", "hi there")
        store.save(s)

        loaded = store.load("db-1")
        assert loaded is not None
        assert loaded.session_id == "db-1"
        assert loaded.name == "test-session"
        assert len(loaded.messages) == 1

    def test_load_missing(self, store):
        assert store.load("ghost") is None

    def test_update_existing(self, store):
        s = HermesSession(session_id="upd", name="v1")
        store.save(s)
        s.name = "v2"
        s.add_message("user", "updated")
        store.save(s)

        loaded = store.load("upd")
        assert loaded.name == "v2"
        assert loaded.message_count == 1

    def test_list_sessions(self, store):
        store.save(HermesSession(session_id="a"))
        store.save(HermesSession(session_id="b"))
        assert set(store.list_sessions()) == {"a", "b"}

    def test_delete(self, store):
        store.save(HermesSession(session_id="del-me"))
        assert store.delete("del-me") is True
        assert store.load("del-me") is None

    def test_delete_missing(self, store):
        assert store.delete("nope") is False

    def test_find_by_name(self, store):
        s = HermesSession(session_id="s1", name="my-session")
        store.save(s)
        found = store.find_by_name("my-session")
        assert found is not None
        assert found.session_id == "s1"

    def test_find_by_name_missing(self, store):
        assert store.find_by_name("no-such-name") is None

    def test_search_sessions(self, store):
        store.save(HermesSession(session_id="a", name="alpha-project"))
        store.save(HermesSession(session_id="b", name="beta-project"))
        store.save(HermesSession(session_id="c", name="gamma-release"))

        results = store.search_sessions("project")
        names = {r["name"] for r in results}
        assert "alpha-project" in names
        assert "beta-project" in names
        assert "gamma-release" not in names

    def test_search_sessions_empty(self, store):
        results = store.search_sessions("nothing")
        assert results == []

    def test_export_markdown(self, store):
        s = HermesSession(session_id="md-1", name="export-test")
        s.add_message("user", "Hello world")
        s.add_message("assistant", "Hi there!")
        store.save(s)

        md = store.export_markdown("md-1")
        assert md is not None
        assert "# Session: export-test" in md
        assert "Hello world" in md
        assert "Hi there!" in md
        assert "**ID**" in md

    def test_export_markdown_missing(self, store):
        assert store.export_markdown("nope") is None

    def test_export_markdown_with_parent(self, store):
        parent = HermesSession(session_id="parent", name="parent-sess")
        child = HermesSession(
            session_id="child", name="child-sess", parent_session_id="parent"
        )
        store.save(parent)
        store.save(child)

        md = store.export_markdown("child")
        assert md is not None
        assert "**Parent**: `parent`" in md

    def test_export_markdown_with_metadata(self, store):
        s = HermesSession(session_id="meta-1", metadata={"env": "prod", "tag": "v2"})
        store.save(s)
        md = store.export_markdown("meta-1")
        assert "## Metadata" in md
        assert "**env**: prod" in md
        assert "**tag**: v2" in md

    def test_update_system_prompt_replace(self, store):
        s = HermesSession(session_id="sp-1")
        s.add_message("system", "original prompt")
        s.add_message("user", "hi")
        store.save(s)

        result = store.update_system_prompt("sp-1", "new prompt")
        assert result is True

        loaded = store.load("sp-1")
        assert loaded.messages[0] == {"role": "system", "content": "new prompt"}
        assert loaded.message_count == 2

    def test_update_system_prompt_prepend(self, store):
        s = HermesSession(session_id="sp-2")
        s.add_message("user", "hi")
        store.save(s)

        result = store.update_system_prompt("sp-2", "system msg")
        assert result is True

        loaded = store.load("sp-2")
        assert loaded.messages[0]["role"] == "system"
        assert loaded.message_count == 2

    def test_update_system_prompt_missing_session(self, store):
        assert store.update_system_prompt("nope", "prompt") is False

    def test_get_detail(self, store):
        s = HermesSession(session_id="det-1", name="detail-test")
        s.add_message("system", "sys")
        s.add_message("user", "hello")
        store.save(s)

        detail = store.get_detail("det-1")
        assert detail is not None
        assert detail["session_id"] == "det-1"
        assert detail["name"] == "detail-test"
        assert detail["message_count"] == 2
        assert detail["last_message"] == {"role": "user", "content": "hello"}
        assert detail["has_system_prompt"] is True

    def test_get_detail_no_system(self, store):
        s = HermesSession(session_id="det-2")
        s.add_message("user", "no system here")
        store.save(s)

        detail = store.get_detail("det-2")
        assert detail["has_system_prompt"] is False

    def test_get_detail_missing(self, store):
        assert store.get_detail("nope") is None

    def test_get_stats(self, store):
        store.save(HermesSession(session_id="st-1"))
        store.save(HermesSession(session_id="st-2"))

        stats = store.get_stats()
        assert stats["session_count"] == 2
        assert stats["db_size_bytes"] == 0  # :memory: has no file
        assert stats["oldest_session_at"] is not None
        assert stats["newest_session_at"] is not None

    def test_get_stats_empty(self, store):
        stats = store.get_stats()
        assert stats["session_count"] == 0

    def test_context_manager(self):
        """Test that __enter__/__exit__ work properly."""
        with SQLiteSessionStore(":memory:") as store:
            store.save(HermesSession(session_id="ctx"))
            assert store.load("ctx") is not None
        # Connection is closed after exit; can't use store here

    def test_persistence_roundtrip_with_messages(self, store):
        """Ensure message content survives serialization."""
        s = HermesSession(session_id="round")
        s.add_message("user", "Special chars: é, ñ, 中文, 🎉")
        s.add_message("assistant", 'JSON-dangerous: "quotes" and \\backslashes\\')
        store.save(s)

        loaded = store.load("round")
        assert loaded.messages[0]["content"] == "Special chars: é, ñ, 中文, 🎉"
        assert '"quotes"' in loaded.messages[1]["content"]

    def test_metadata_persistence(self, store):
        s = HermesSession(session_id="meta-persist")
        s.metadata = {"nested": {"a": 1, "b": [1, 2, 3]}, "flag": True}
        store.save(s)

        loaded = store.load("meta-persist")
        assert loaded.metadata["nested"]["a"] == 1
        assert loaded.metadata["nested"]["b"] == [1, 2, 3]
        assert loaded.metadata["flag"] is True

    def test_prune_old_sessions_nothing_to_prune(self, store):
        store.save(HermesSession(session_id="recent"))
        pruned = store.prune_old_sessions(days_old=30)
        assert pruned == 0

    def test_prune_old_sessions_archives(self, tmp_path):
        """Test that old sessions are archived to gzipped JSON."""
        db_path = tmp_path / "test.db"
        with SQLiteSessionStore(str(db_path)) as store:
            old_session = HermesSession(session_id="old-1", name="ancient")
            old_session.updated_at = time.time() - (60 * 86400)  # 60 days ago
            store.save(old_session)

            pruned = store.prune_old_sessions(days_old=30)
            assert pruned == 1

            # Verify archive file exists
            archive_dir = tmp_path / "sessions_archive"
            archive_file = archive_dir / "old-1.json.gz"
            assert archive_file.exists()

            # Verify archive content
            with gzip.open(archive_file, "rt", encoding="utf-8") as f:
                data = json.load(f)
            assert data["session_id"] == "old-1"
            assert data["name"] == "ancient"

            # Verify deleted from DB
            assert store.load("old-1") is None

    def test_fts_search(self, store):
        s = HermesSession(session_id="fts-1", name="code review")
        s.add_message("user", "Please review this Python function for bugs")
        store.save(s)

        results = store.search_fts("Python")
        assert len(results) >= 1
        assert any(r["session_id"] == "fts-1" for r in results)

    def test_fts_search_no_results(self, store):
        store.save(HermesSession(session_id="fts-2", name="test"))
        results = store.search_fts("zzznonexistentzzz")
        assert len(results) == 0

    def test_multiple_sessions_isolation(self, store):
        """Ensure sessions don't leak data between each other."""
        s1 = HermesSession(session_id="iso-1", name="first")
        s1.add_message("user", "secret-data-1")
        s2 = HermesSession(session_id="iso-2", name="second")
        s2.add_message("user", "secret-data-2")

        store.save(s1)
        store.save(s2)

        loaded1 = store.load("iso-1")
        loaded2 = store.load("iso-2")
        assert loaded1.messages[0]["content"] == "secret-data-1"
        assert loaded2.messages[0]["content"] == "secret-data-2"

    def test_file_based_store(self, tmp_path):
        """Test SQLiteSessionStore with a real file path."""
        db_file = tmp_path / "sessions.db"
        with SQLiteSessionStore(str(db_file)) as store:
            s = HermesSession(session_id="file-1", name="persistent")
            s.add_message("user", "hello from file")
            store.save(s)

        # Re-open and verify persistence
        with SQLiteSessionStore(str(db_file)) as store:
            loaded = store.load("file-1")
            assert loaded is not None
            assert loaded.name == "persistent"
            assert loaded.messages[0]["content"] == "hello from file"

    def test_schema_migration_adds_columns(self, tmp_path):
        """Test that migration adds name/parent_session_id to old schemas."""
        import sqlite3

        db_file = tmp_path / "old.db"
        # Create an old-style DB without the new columns
        conn = sqlite3.connect(str(db_file))
        conn.execute("""
            CREATE TABLE hermes_sessions (
                session_id TEXT PRIMARY KEY,
                messages TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        conn.execute(
            "INSERT INTO hermes_sessions VALUES (?, ?, ?, ?, ?)",
            ("old-sess", "[]", "{}", time.time(), time.time()),
        )
        conn.commit()
        conn.close()

        # Open with SQLiteSessionStore — migration should add columns
        with SQLiteSessionStore(str(db_file)) as store:
            loaded = store.load("old-sess")
            assert loaded is not None
            assert loaded.name is None  # Column added but NULL
            assert loaded.parent_session_id is None
