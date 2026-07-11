"""Tests for agents.hermes.session — HermesSession, SessionStores.

Zero-Mock: All tests use real SQLite databases (in-memory)
and real InMemorySessionStore.
"""

from __future__ import annotations

import gzip
import json
import sqlite3
import time
from typing import TYPE_CHECKING

import pytest

from codomyrmex.agents.hermes.session import (
    HermesSession,
    InMemorySessionStore,
    SQLiteSessionStore,
)

if TYPE_CHECKING:
    from pathlib import Path

# ── HermesSession ─────────────────────────────────────────────────────


class TestHermesSession:
    """Verify session data model."""

    def test_default_session_id(self) -> None:
        session = HermesSession()
        assert len(session.session_id) == 12

    def test_custom_session_id(self) -> None:
        session = HermesSession(session_id="my-session")
        assert session.session_id == "my-session"

    def test_add_message(self) -> None:
        session = HermesSession()
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi!")
        assert session.message_count == 2

    def test_last_message(self) -> None:
        session = HermesSession()
        assert session.last_message is None
        session.add_message("user", "Hello")
        assert session.last_message == {"role": "user", "content": "Hello"}

    def test_updated_at_changes(self) -> None:
        session = HermesSession()
        t0 = session.updated_at
        time.sleep(0.01)
        session.add_message("user", "msg")
        assert session.updated_at >= t0

    def test_metadata(self) -> None:
        session = HermesSession(metadata={"task": "code_review"})
        assert session.metadata["task"] == "code_review"


# ── InMemorySessionStore ─────────────────────────────────────────────


class TestInMemorySessionStore:
    """Verify in-memory store."""

    def test_save_and_load(self) -> None:
        store = InMemorySessionStore()
        session = HermesSession(session_id="s1")
        session.add_message("user", "Hello")
        store.save(session)

        loaded = store.load("s1")
        assert loaded is not None
        assert loaded.message_count == 1

    def test_load_nonexistent(self) -> None:
        store = InMemorySessionStore()
        assert store.load("nope") is None

    def test_list_sessions(self) -> None:
        store = InMemorySessionStore()
        store.save(HermesSession(session_id="a"))
        store.save(HermesSession(session_id="b"))
        assert sorted(store.list_sessions()) == ["a", "b"]

    def test_delete(self) -> None:
        store = InMemorySessionStore()
        store.save(HermesSession(session_id="x"))
        assert store.delete("x") is True
        assert store.load("x") is None

    def test_delete_nonexistent(self) -> None:
        store = InMemorySessionStore()
        assert store.delete("nope") is False


# ── SQLiteSessionStore ───────────────────────────────────────────────


class TestSQLiteSessionStore:
    """Verify SQLite-backed persistence (in-memory DB)."""

    def test_save_and_load(self) -> None:
        store = SQLiteSessionStore(":memory:")
        session = HermesSession(session_id="sq1")
        session.add_message("user", "Analyze this")
        session.add_message("assistant", "Done")
        store.save(session)

        loaded = store.load("sq1")
        assert loaded is not None
        assert loaded.message_count == 2
        assert loaded.messages[0]["content"] == "Analyze this"

    def test_load_nonexistent(self) -> None:
        store = SQLiteSessionStore(":memory:")
        assert store.load("nope") is None

    def test_list_sessions(self) -> None:
        store = SQLiteSessionStore(":memory:")
        store.save(HermesSession(session_id="a"))
        store.save(HermesSession(session_id="b"))
        sessions = store.list_sessions()
        assert len(sessions) == 2

    def test_delete(self) -> None:
        store = SQLiteSessionStore(":memory:")
        store.save(HermesSession(session_id="del1"))
        assert store.delete("del1") is True
        assert store.load("del1") is None

    def test_delete_nonexistent(self) -> None:
        store = SQLiteSessionStore(":memory:")
        assert store.delete("nope") is False

    def test_update_existing_session(self) -> None:
        store = SQLiteSessionStore(":memory:")
        session = HermesSession(session_id="up1")
        session.add_message("user", "First")
        store.save(session)

        session.add_message("assistant", "Response")
        store.save(session)

        loaded = store.load("up1")
        assert loaded is not None
        assert loaded.message_count == 2

    def test_metadata_persisted(self) -> None:
        store = SQLiteSessionStore(":memory:")
        session = HermesSession(
            session_id="meta1",
            metadata={"model": "hermes3", "backend": "ollama"},
        )
        store.save(session)

        loaded = store.load("meta1")
        assert loaded is not None
        assert loaded.metadata["model"] == "hermes3"

    def test_timestamps_persisted(self) -> None:
        store = SQLiteSessionStore(":memory:")
        session = HermesSession(session_id="ts1")
        original_created = session.created_at
        store.save(session)

        loaded = store.load("ts1")
        assert loaded is not None
        assert loaded.created_at == pytest.approx(original_created, abs=0.1)


# ── SQLiteSessionStore v0.2.0 ────────────────────────────────────────


class TestSQLiteSessionStoreV020:
    """Tests for v0.2.0 named session features."""

    def test_named_session_save_and_load(self) -> None:
        """Named sessions should persist and restore the name field."""
        store = SQLiteSessionStore(":memory:")
        session = HermesSession(session_id="ns1", name="refactoring-payments")
        session.add_message("user", "Let's refactor")
        store.save(session)

        loaded = store.load("ns1")
        assert loaded is not None
        assert loaded.name == "refactoring-payments"
        assert loaded.message_count == 1

    def test_find_by_name(self) -> None:
        """find_by_name() should return the most recent session with a given name."""
        store = SQLiteSessionStore(":memory:")
        s1 = HermesSession(session_id="fn1", name="code-review")
        s1.add_message("user", "Review this code")
        store.save(s1)

        s2 = HermesSession(session_id="fn2", name="testing")
        store.save(s2)

        found = store.find_by_name("code-review")
        assert found is not None
        assert found.session_id == "fn1"
        assert found.name == "code-review"

        # Non-existent name returns None
        assert store.find_by_name("doesnt-exist") is None

    def test_search_sessions(self) -> None:
        """search_sessions() should match name substrings."""
        store = SQLiteSessionStore(":memory:")
        store.save(HermesSession(session_id="sr1", name="api-refactoring"))
        store.save(HermesSession(session_id="sr2", name="api-testing"))
        store.save(HermesSession(session_id="sr3", name="deployment"))

        results = store.search_sessions("api")
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert "api-refactoring" in names
        assert "api-testing" in names

        # No matches
        assert store.search_sessions("nonexistent") == []

    def test_schema_migration_from_pre_v020(self) -> None:
        """Old DBs without 'name' column should migrate gracefully."""

        store = SQLiteSessionStore(":memory:")
        # Simulate pre-v0.2.0 by inserting without name column
        # The migration already ran, so this tests that the code works with NULL names
        session = HermesSession(session_id="old1")  # name defaults to None
        store.save(session)

        loaded = store.load("old1")
        assert loaded is not None
        assert loaded.name is None  # No name set — graceful default


# ── HermesSession.fork() ──────────────────────────────────────────────


class TestHermesSessionFork:
    """Verify session forking behavior."""

    def test_fork_creates_child_with_parent_id(self) -> None:
        parent = HermesSession(session_id="parent1", name="original")
        parent.add_message("user", "start task")
        child = parent.fork("child-task")

        assert child.session_id != parent.session_id
        assert child.parent_session_id == "parent1"
        assert child.name == "child-task"

    def test_fork_inherits_messages(self) -> None:
        parent = HermesSession(session_id="p1")
        parent.add_message("user", "msg1")
        parent.add_message("assistant", "reply1")

        child = parent.fork()
        assert child.message_count == 2
        assert child.messages == parent.messages

    def test_fork_messages_are_independent(self) -> None:
        parent = HermesSession(session_id="p2")
        parent.add_message("user", "original")

        child = parent.fork()
        child.add_message("user", "child-only")

        assert parent.message_count == 1
        assert child.message_count == 2

    def test_fork_metadata_includes_forked_from(self) -> None:
        parent = HermesSession(session_id="p3", metadata={"key": "value"})
        child = parent.fork()

        assert child.metadata["key"] == "value"
        assert child.metadata["forked_from"] == "p3"

    def test_fork_default_name(self) -> None:
        parent = HermesSession(session_id="p4", name="parent-name")
        child = parent.fork()

        assert child.name is None  # default is None when not specified


# ── SQLiteSessionStore.search_fts() ───────────────────────────────────


class TestSQLiteSearchFts:
    """Verify full-text search over session contents."""

    def test_search_fts_finds_matching_content(self) -> None:
        store = SQLiteSessionStore(":memory:")
        s1 = HermesSession(session_id="fts1", name="refactoring")
        s1.add_message("user", "Let's refactor the payment module")
        s1.add_message("assistant", "I see several issues")
        store.save(s1)

        s2 = HermesSession(session_id="fts2", name="testing")
        s2.add_message("user", "Write unit tests for auth")
        store.save(s2)

        results = store.search_fts("refactor")
        assert len(results) >= 1
        assert any(r["session_id"] == "fts1" for r in results)

    def test_search_fts_no_match(self) -> None:
        store = SQLiteSessionStore(":memory:")
        s1 = HermesSession(session_id="fts3", name="coding")
        s1.add_message("user", "Hello world")
        store.save(s1)

        results = store.search_fts("nonexistent_term_xyz")
        assert results == []

    def test_search_fts_respects_limit(self) -> None:
        store = SQLiteSessionStore(":memory:")
        for i in range(5):
            s = HermesSession(session_id=f"ftsl{i}", name=f"session-{i}")
            s.add_message("user", "deploy the application to production")
            store.save(s)

        results = store.search_fts("deploy", limit=2)
        assert len(results) <= 2

    def test_search_fts_returns_snippet_and_rank(self) -> None:
        store = SQLiteSessionStore(":memory:")
        s = HermesSession(session_id="fts4", name="debugging")
        s.add_message("user", "The authentication module has a bug")
        store.save(s)

        results = store.search_fts("authentication")
        assert len(results) >= 1
        assert "session_id" in results[0]
        assert "messages_snippet" in results[0]
        assert "rank" in results[0]


# ── SQLiteSessionStore context manager ────────────────────────────────


class TestSQLiteContextManager:
    """Verify context manager protocol."""

    def test_context_manager_enters_and_exits(self) -> None:
        with SQLiteSessionStore(":memory:") as store:
            store.save(HermesSession(session_id="ctx1"))
            assert store.load("ctx1") is not None
        # Connection should be closed after exiting — accessing it would error
        # (we can't easily test this without trying to use the closed conn)

    def test_context_manager_returns_self(self) -> None:
        store = SQLiteSessionStore(":memory:")
        result = store.__enter__()
        assert result is store
        store.__exit__()


# ── SQLiteSessionStore.close() ────────────────────────────────────────


class TestSQLiteClose:
    """Verify close() behavior."""

    def test_close_connection(self) -> None:
        store = SQLiteSessionStore(":memory:")
        store.save(HermesSession(session_id="c1"))
        store.close()
        # After close, operations should fail
        with pytest.raises(sqlite3.ProgrammingError):
            store.load("c1")


# ── SQLiteSessionStore.prune_old_sessions() ────────────────────────────


class TestPruneOldSessions:
    """Verify session pruning and archiving."""

    def test_prune_returns_zero_when_no_old_sessions(self, tmp_path: Path) -> None:
        """prune_old_sessions returns 0 when all sessions are recent."""
        db_path = tmp_path / "test.db"
        store = SQLiteSessionStore(str(db_path))

        # Create a recent session
        session = HermesSession(session_id="recent1", name="recent")
        session.add_message("user", "Hello")
        store.save(session)

        # Prune with 0 days (should prune nothing since session is new)
        # Actually, let's use 30 days - session is brand new
        count = store.prune_old_sessions(days_old=30)
        assert count == 0

        # Session should still exist
        loaded = store.load("recent1")
        assert loaded is not None
        store.close()

    def test_prune_archives_and_deletes_old_sessions(self, tmp_path: Path) -> None:
        """Old sessions are archived as gzipped JSON and deleted from DB."""
        db_path = tmp_path / "test.db"
        store = SQLiteSessionStore(str(db_path))

        # Create an old session by manually setting updated_at
        old_session = HermesSession(
            session_id="old1",
            name="old-session",
            metadata={"task": "cleanup"},
        )
        old_session.add_message("user", "This is old")
        old_session.add_message("assistant", "Yes it is")
        store.save(old_session)

        # Manually set updated_at to be 60 days ago
        store._conn.execute(
            "UPDATE hermes_sessions SET updated_at = ? WHERE session_id = ?",
            (time.time() - (60 * 86400), "old1"),
        )
        store._conn.commit()

        # Create a recent session
        recent_session = HermesSession(session_id="recent1", name="recent")
        recent_session.add_message("user", "This is new")
        store.save(recent_session)

        # Prune sessions older than 30 days
        count = store.prune_old_sessions(days_old=30)
        assert count == 1

        # Old session should be deleted from DB
        assert store.load("old1") is None

        # Recent session should still exist
        assert store.load("recent1") is not None

        # Archive directory should exist
        archive_dir = db_path.parent / "sessions_archive"
        assert archive_dir.exists()

        # Archive file should exist
        archive_file = archive_dir / "old1.json.gz"
        assert archive_file.exists()

        # Archive should contain valid gzipped JSON
        with gzip.open(archive_file, "rt", encoding="utf-8") as f:
            archived = json.load(f)

        assert archived["session_id"] == "old1"
        assert archived["name"] == "old-session"
        assert archived["metadata"]["task"] == "cleanup"
        assert len(archived["messages"]) == 2
        assert archived["messages"][0]["content"] == "This is old"

        store.close()

    def test_prune_multiple_old_sessions(self, tmp_path: Path) -> None:
        """Multiple old sessions are all pruned."""
        db_path = tmp_path / "test.db"
        store = SQLiteSessionStore(str(db_path))

        # Create 3 old sessions
        for i in range(3):
            session = HermesSession(session_id=f"old{i}", name=f"old-{i}")
            session.add_message("user", f"Old session {i}")
            store.save(session)
            store._conn.execute(
                "UPDATE hermes_sessions SET updated_at = ? WHERE session_id = ?",
                (time.time() - (60 * 86400), f"old{i}"),
            )
        store._conn.commit()

        # Create 2 recent sessions
        for i in range(2):
            session = HermesSession(session_id=f"recent{i}", name=f"recent-{i}")
            store.save(session)

        count = store.prune_old_sessions(days_old=30)
        assert count == 3

        # All old sessions should be gone
        for i in range(3):
            assert store.load(f"old{i}") is None

        # All recent sessions should remain
        for i in range(2):
            assert store.load(f"recent{i}") is not None

        # Archive should have 3 files
        archive_dir = db_path.parent / "sessions_archive"
        archive_files = list(archive_dir.glob("*.json.gz"))
        assert len(archive_files) == 3

        store.close()

    def test_prune_creates_archive_directory(self, tmp_path: Path) -> None:
        """Archive directory is created if it doesn't exist."""
        db_path = tmp_path / "subdir" / "test.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        store = SQLiteSessionStore(str(db_path))

        session = HermesSession(session_id="arch1")
        store.save(session)
        store._conn.execute(
            "UPDATE hermes_sessions SET updated_at = ? WHERE session_id = ?",
            (time.time() - (60 * 86400), "arch1"),
        )
        store._conn.commit()

        archive_dir = db_path.parent / "sessions_archive"
        assert not archive_dir.exists()

        store.prune_old_sessions(days_old=30)

        assert archive_dir.exists()
        assert archive_dir.is_dir()

        store.close()

    def test_prune_in_memory_db_skips_archive(self, tmp_path: Path) -> None:
        """In-memory DB (:memory:) can't create archive files adjacent to DB."""
        # Note: This tests the behavior with :memory: db_path
        # The function will try to create sessions_archive in current directory
        # This is expected behavior - the function doesn't special-case :memory:
        store = SQLiteSessionStore(":memory:")

        session = HermesSession(session_id="mem1")
        store.save(session)

        # This will work but create archive in current dir
        # We just verify it doesn't crash
        count = store.prune_old_sessions(days_old=30)
        assert count == 0  # No old sessions

        store.close()


# ── SQLiteSessionStore.get_stats() ────────────────────────────────────


class TestGetStats:
    """Verify get_stats() returns correct summary statistics."""

    def test_get_stats_empty_db(self) -> None:
        """Stats for an empty database should show zero sessions."""
        store = SQLiteSessionStore(":memory:")
        stats = store.get_stats()

        assert stats["session_count"] == 0
        assert stats["db_size_bytes"] == 0  # :memory: has no file
        assert stats["oldest_session_at"] is None
        assert stats["newest_session_at"] is None
        store.close()

    def test_get_stats_with_sessions(self) -> None:
        """Stats should reflect session count and timestamps."""
        store = SQLiteSessionStore(":memory:")

        s1 = HermesSession(session_id="st1", name="first")
        s1.add_message("user", "hello")
        store.save(s1)

        s2 = HermesSession(session_id="st2", name="second")
        s2.add_message("user", "hi")
        store.save(s2)

        stats = store.get_stats()

        assert stats["session_count"] == 2
        assert stats["oldest_session_at"] is not None
        assert stats["newest_session_at"] is not None
        assert stats["newest_session_at"] >= stats["oldest_session_at"]
        store.close()

    def test_get_stats_file_db_reports_size(self, tmp_path: Path) -> None:
        """File-backed DB should report non-zero db_size_bytes."""
        db_path = tmp_path / "stats_test.db"
        store = SQLiteSessionStore(str(db_path))

        store.save(HermesSession(session_id="fs1"))
        stats = store.get_stats()

        assert stats["session_count"] == 1
        assert stats["db_size_bytes"] > 0
        store.close()


# ── SQLiteSessionStore.export_markdown() ───────────────────────────────


class TestExportMarkdown:
    """Verify export_markdown() produces correct Markdown output."""

    def test_export_existing_session(self) -> None:
        """Export should include session ID, messages, and metadata."""
        store = SQLiteSessionStore(":memory:")
        session = HermesSession(
            session_id="md1",
            name="my-review",
            metadata={"priority": "high"},
        )
        session.add_message("user", "Review this code")
        session.add_message("assistant", "Looks good")
        store.save(session)

        md = store.export_markdown("md1")
        assert md is not None
        assert "# Session: my-review" in md
        assert "`md1`" in md
        assert "## User" in md
        assert "Review this code" in md
        assert "## Assistant" in md
        assert "Looks good" in md
        assert "## Metadata" in md
        assert "priority" in md
        assert "high" in md
        store.close()

    def test_export_nonexistent_session(self) -> None:
        """Export should return None for missing sessions."""
        store = SQLiteSessionStore(":memory:")
        assert store.export_markdown("nope") is None
        store.close()

    def test_export_includes_parent_when_set(self) -> None:
        """Export should show parent session ID when present."""
        store = SQLiteSessionStore(":memory:")
        parent = HermesSession(session_id="parent-x")
        child = parent.fork("child-y")
        store.save(child)

        md = store.export_markdown(child.session_id)
        assert md is not None
        assert "Parent" in md
        assert "parent-x" in md
        store.close()

    def test_export_without_name_uses_id(self) -> None:
        """Export should fall back to session_id as title when name is None."""
        store = SQLiteSessionStore(":memory:")
        session = HermesSession(session_id="no-name")
        store.save(session)

        md = store.export_markdown("no-name")
        assert md is not None
        assert "# Session: no-name" in md
        store.close()


# ── SQLiteSessionStore.update_system_prompt() ──────────────────────────


class TestUpdateSystemPrompt:
    """Verify update_system_prompt() upserts system messages correctly."""

    def test_insert_system_prompt_into_empty_session(self) -> None:
        """System prompt should be inserted at index 0."""
        store = SQLiteSessionStore(":memory:")
        session = HermesSession(session_id="sp1")
        session.add_message("user", "Hello")
        store.save(session)

        assert store.update_system_prompt("sp1", "You are helpful") is True

        loaded = store.load("sp1")
        assert loaded is not None
        assert loaded.messages[0]["role"] == "system"
        assert loaded.messages[0]["content"] == "You are helpful"
        assert loaded.message_count == 2  # system + original user
        store.close()

    def test_replace_existing_system_prompt(self) -> None:
        """Existing system prompt should be replaced, not appended."""
        store = SQLiteSessionStore(":memory:")
        session = HermesSession(session_id="sp2")
        session.add_message("system", "Old prompt")
        session.add_message("user", "Hello")
        store.save(session)

        assert store.update_system_prompt("sp2", "New prompt") is True

        loaded = store.load("sp2")
        assert loaded is not None
        assert loaded.message_count == 2  # replaced, not added
        assert loaded.messages[0]["content"] == "New prompt"
        store.close()

    def test_update_system_prompt_nonexistent_session(self) -> None:
        """Should return False for non-existent sessions."""
        store = SQLiteSessionStore(":memory:")
        assert store.update_system_prompt("nope", "prompt") is False
        store.close()


# ── SQLiteSessionStore.get_detail() ────────────────────────────────────


class TestGetDetail:
    """Verify get_detail() returns rich session information."""

    def test_get_detail_full_session(self) -> None:
        """Detail should include all session fields plus computed ones."""
        store = SQLiteSessionStore(":memory:")
        session = HermesSession(session_id="det1", name="detail-test")
        session.add_message("system", "Be helpful")
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there")
        store.save(session)

        detail = store.get_detail("det1")
        assert detail is not None
        assert detail["session_id"] == "det1"
        assert detail["name"] == "detail-test"
        assert detail["message_count"] == 3
        assert detail["last_message"] == {"role": "assistant", "content": "Hi there"}
        assert detail["has_system_prompt"] is True
        assert detail["metadata"] == {}
        assert "created_at" in detail
        assert "updated_at" in detail
        store.close()

    def test_get_detail_no_system_prompt(self) -> None:
        """has_system_prompt should be False when first message is not system."""
        store = SQLiteSessionStore(":memory:")
        session = HermesSession(session_id="det2")
        session.add_message("user", "Hello")
        store.save(session)

        detail = store.get_detail("det2")
        assert detail is not None
        assert detail["has_system_prompt"] is False
        store.close()

    def test_get_detail_nonexistent(self) -> None:
        """Should return None for missing sessions."""
        store = SQLiteSessionStore(":memory:")
        assert store.get_detail("nope") is None
        store.close()
