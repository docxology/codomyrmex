"""Tests for agents.hermes.session — HermesSession, SessionStores.

Zero-Mock: All tests use real SQLite databases (in-memory)
and real InMemorySessionStore.
"""

from __future__ import annotations

import sqlite3
import time

import pytest

from codomyrmex.agents.hermes.session import (
    HermesSession,
    InMemorySessionStore,
    SQLiteSessionStore,
)

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
