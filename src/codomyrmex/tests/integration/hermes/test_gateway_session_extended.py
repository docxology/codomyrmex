"""Integration tests for new HermesClient session management methods.

Tests ``get_session_stats``, ``fork_session``, ``export_session_markdown``,
``set_system_prompt``, ``get_session_detail``, and the underlying
``SQLiteSessionStore`` helpers.

Zero-mock policy: all tests use real ``SQLiteSessionStore`` (in-memory).
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def inmem_store() -> SQLiteSessionStore:
    store = SQLiteSessionStore(":memory:")
    yield store
    store.close()


def _make_session(store: SQLiteSessionStore, name: str | None = None) -> HermesSession:
    session = HermesSession(name=name)
    session.add_message("user", "hello")
    session.add_message("assistant", "world")
    store.save(session)
    return session


# ---------------------------------------------------------------------------
# get_stats
# ---------------------------------------------------------------------------


class TestGetStats:
    def test_empty_db_returns_zero_count(self, inmem_store: SQLiteSessionStore) -> None:
        stats = inmem_store.get_stats()
        assert stats["session_count"] == 0
        assert stats["oldest_session_at"] is None
        assert stats["newest_session_at"] is None

    def test_stats_count_matches_saved_sessions(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        for i in range(3):
            _make_session(inmem_store, name=f"sess-{i}")
        stats = inmem_store.get_stats()
        assert stats["session_count"] == 3

    def test_in_memory_db_size_is_zero(self, inmem_store: SQLiteSessionStore) -> None:
        _make_session(inmem_store)
        stats = inmem_store.get_stats()
        # In-memory stores always report 0 bytes
        assert stats["db_size_bytes"] == 0

    def test_file_db_size_is_positive(self, tmp_path):
        db = tmp_path / "test.db"
        with SQLiteSessionStore(db) as store:
            _make_session(store)
            stats = store.get_stats()
        assert stats["db_size_bytes"] > 0

    def test_timestamps_set_after_save(self, inmem_store: SQLiteSessionStore) -> None:
        s = _make_session(inmem_store)
        stats = inmem_store.get_stats()
        assert stats["oldest_session_at"] == pytest.approx(s.created_at, abs=1)
        assert stats["newest_session_at"] == pytest.approx(s.updated_at, abs=1)


# ---------------------------------------------------------------------------
# fork (via HermesSession.fork)
# ---------------------------------------------------------------------------


class TestFork:
    def test_fork_inherits_messages(self, inmem_store: SQLiteSessionStore) -> None:
        parent = _make_session(inmem_store, name="parent")
        child = parent.fork(new_name="child")
        inmem_store.save(child)

        loaded = inmem_store.load(child.session_id)
        assert loaded is not None
        assert loaded.messages == parent.messages

    def test_fork_has_correct_parent_id(self, inmem_store: SQLiteSessionStore) -> None:
        parent = _make_session(inmem_store, name="orig")
        child = parent.fork()
        assert child.parent_session_id == parent.session_id

    def test_fork_has_independent_session_id(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        parent = _make_session(inmem_store)
        child = parent.fork()
        assert child.session_id != parent.session_id

    def test_fork_messages_are_independent_copy(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        parent = _make_session(inmem_store)
        child = parent.fork()
        child.add_message("user", "extra message")
        assert len(child.messages) == len(parent.messages) + 1


# ---------------------------------------------------------------------------
# export_markdown
# ---------------------------------------------------------------------------


class TestExportMarkdown:
    def test_missing_session_returns_none(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        result = inmem_store.export_markdown("nonexistent")
        assert result is None

    def test_export_contains_h1_title(self, inmem_store: SQLiteSessionStore) -> None:
        s = _make_session(inmem_store, name="My Session")
        md = inmem_store.export_markdown(s.session_id)
        assert md is not None
        assert "# Session: My Session" in md

    def test_export_contains_user_and_assistant_headings(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        s = _make_session(inmem_store)
        md = inmem_store.export_markdown(s.session_id)
        assert "## User" in md
        assert "## Assistant" in md

    def test_export_contains_message_content(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        s = HermesSession()
        s.add_message("user", "unique_prompt_content_99")
        inmem_store.save(s)
        md = inmem_store.export_markdown(s.session_id)
        assert "unique_prompt_content_99" in md

    def test_export_contains_session_id(self, inmem_store: SQLiteSessionStore) -> None:
        s = _make_session(inmem_store)
        md = inmem_store.export_markdown(s.session_id)
        assert s.session_id in md


# ---------------------------------------------------------------------------
# update_system_prompt
# ---------------------------------------------------------------------------


class TestUpdateSystemPrompt:
    def test_returns_false_for_missing_session(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        result = inmem_store.update_system_prompt("ghost", "something")
        assert result is False

    def test_prepends_system_message(self, inmem_store: SQLiteSessionStore) -> None:
        s = _make_session(inmem_store)
        ok = inmem_store.update_system_prompt(s.session_id, "You are a pirate.")
        assert ok is True
        loaded = inmem_store.load(s.session_id)
        assert loaded.messages[0]["role"] == "system"
        assert "pirate" in loaded.messages[0]["content"]

    def test_replaces_existing_system_message(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        s = HermesSession()
        s.add_message("system", "old instruction")
        s.add_message("user", "hello")
        inmem_store.save(s)

        inmem_store.update_system_prompt(s.session_id, "new instruction")
        loaded = inmem_store.load(s.session_id)
        # Still only one system message
        sys_msgs = [m for m in loaded.messages if m["role"] == "system"]
        assert len(sys_msgs) == 1
        assert "new instruction" in sys_msgs[0]["content"]

    def test_existing_user_messages_preserved(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        s = _make_session(inmem_store)
        original_count = len(s.messages)
        inmem_store.update_system_prompt(s.session_id, "sys")
        loaded = inmem_store.load(s.session_id)
        assert len(loaded.messages) == original_count + 1  # +1 for system prompt


# ---------------------------------------------------------------------------
# get_detail
# ---------------------------------------------------------------------------


class TestGetDetail:
    def test_missing_session_returns_none(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        detail = inmem_store.get_detail("no_such_session")
        assert detail is None

    def test_detail_contains_expected_keys(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        s = _make_session(inmem_store, "test-detail")
        detail = inmem_store.get_detail(s.session_id)
        assert detail is not None
        for key in (
            "session_id",
            "name",
            "message_count",
            "last_message",
            "has_system_prompt",
            "metadata",
        ):
            assert key in detail

    def test_message_count_correct(self, inmem_store: SQLiteSessionStore) -> None:
        s = _make_session(inmem_store)
        detail = inmem_store.get_detail(s.session_id)
        assert detail["message_count"] == 2

    def test_has_system_prompt_false_by_default(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        s = _make_session(inmem_store)
        detail = inmem_store.get_detail(s.session_id)
        assert detail["has_system_prompt"] is False

    def test_has_system_prompt_true_after_update(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        s = _make_session(inmem_store)
        inmem_store.update_system_prompt(s.session_id, "sys")
        detail = inmem_store.get_detail(s.session_id)
        assert detail["has_system_prompt"] is True

    def test_last_message_returns_most_recent(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        s = _make_session(inmem_store)
        detail = inmem_store.get_detail(s.session_id)
        assert detail["last_message"] is not None
        assert detail["last_message"]["role"] == "assistant"


# ---------------------------------------------------------------------------
# prune_old_sessions (already tested in test_gateway_session_gc.py — add edge cases)
# ---------------------------------------------------------------------------


class TestPruneEdgeCases:
    def test_prune_zero_returns_zero_when_none_old(
        self, inmem_store: SQLiteSessionStore
    ) -> None:
        _make_session(inmem_store)
        # Sessions just created — not older than 365 days
        count = inmem_store.prune_old_sessions(days_old=365)
        assert count == 0

    def test_prune_with_threshold_zero_removes_all(self, tmp_path) -> None:
        db = tmp_path / "prune.db"
        with SQLiteSessionStore(db) as store:
            for _ in range(3):
                s = HermesSession()
                s.updated_at = time.time() - 9999  # very old
                store.save(s)
            removed = store.prune_old_sessions(days_old=0)
        assert removed == 3
