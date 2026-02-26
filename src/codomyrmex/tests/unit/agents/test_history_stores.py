"""Unit tests for codomyrmex.agents.history.stores module.

Tests InMemoryHistoryStore, FileHistoryStore, and SQLiteHistoryStore.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from codomyrmex.agents.history.models import (
    Conversation,
    HistoryMessage,
    MessageRole,
)
from codomyrmex.agents.history.stores import (
    FileHistoryStore,
    InMemoryHistoryStore,
    SQLiteHistoryStore,
)


def _make_conversation(
    conv_id: str = "test-conv-1",
    title: str = "Test Conversation",
    messages: list[tuple[MessageRole, str]] | None = None,
    updated_at: datetime | None = None,
) -> Conversation:
    """Helper to build a Conversation with optional messages."""
    conv = Conversation(
        conversation_id=conv_id,
        title=title,
        updated_at=updated_at or datetime.now(),
    )
    for role, content in (messages or []):
        conv.add_message(role, content)
    return conv


# ────────────────────────────────────────────────────────────────────
# InMemoryHistoryStore
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestInMemoryHistoryStore:
    """Tests for InMemoryHistoryStore."""

    def test_save_and_load(self):
        """Save then load returns the same conversation."""
        store = InMemoryHistoryStore()
        conv = _make_conversation()
        store.save(conv)
        loaded = store.load(conv.conversation_id)
        assert loaded is conv

    def test_load_nonexistent_returns_none(self):
        """Loading a missing conversation returns None."""
        store = InMemoryHistoryStore()
        assert store.load("does-not-exist") is None

    def test_delete_existing(self):
        """Deleting an existing conversation returns True."""
        store = InMemoryHistoryStore()
        conv = _make_conversation()
        store.save(conv)
        assert store.delete(conv.conversation_id) is True
        assert store.load(conv.conversation_id) is None

    def test_delete_nonexistent(self):
        """Deleting a missing conversation returns False."""
        store = InMemoryHistoryStore()
        assert store.delete("ghost") is False

    def test_list_conversations_sorted_by_updated_at(self):
        """list_conversations returns most recent first."""
        store = InMemoryHistoryStore()
        now = datetime.now()
        c1 = _make_conversation("c1", updated_at=now - timedelta(hours=2))
        c2 = _make_conversation("c2", updated_at=now - timedelta(hours=1))
        c3 = _make_conversation("c3", updated_at=now)
        store.save(c1)
        store.save(c2)
        store.save(c3)
        result = store.list_conversations()
        assert [c.conversation_id for c in result] == ["c3", "c2", "c1"]

    def test_list_conversations_limit_and_offset(self):
        """list_conversations respects limit and offset."""
        store = InMemoryHistoryStore()
        now = datetime.now()
        for i in range(5):
            store.save(_make_conversation(f"c{i}", updated_at=now - timedelta(hours=i)))
        result = store.list_conversations(limit=2, offset=1)
        assert len(result) == 2
        assert result[0].conversation_id == "c1"
        assert result[1].conversation_id == "c2"

    def test_search_by_title(self):
        """search matches conversation titles."""
        store = InMemoryHistoryStore()
        store.save(_make_conversation("c1", title="Code Review"))
        store.save(_make_conversation("c2", title="Design Discussion"))
        results = store.search("review")
        assert len(results) == 1
        assert results[0].conversation_id == "c1"

    def test_search_by_message_content(self):
        """search matches message content."""
        store = InMemoryHistoryStore()
        conv = _make_conversation(
            "c1",
            title="General",
            messages=[(MessageRole.USER, "Fix the authentication bug")],
        )
        store.save(conv)
        results = store.search("authentication")
        assert len(results) == 1

    def test_search_case_insensitive(self):
        """search is case-insensitive."""
        store = InMemoryHistoryStore()
        store.save(_make_conversation("c1", title="IMPORTANT Meeting"))
        results = store.search("important")
        assert len(results) == 1

    def test_search_no_match(self):
        """search returns empty when nothing matches."""
        store = InMemoryHistoryStore()
        store.save(_make_conversation("c1", title="Planning"))
        results = store.search("xyznonexistent")
        assert results == []

    def test_clear(self):
        """clear removes all conversations."""
        store = InMemoryHistoryStore()
        store.save(_make_conversation("c1"))
        store.save(_make_conversation("c2"))
        store.clear()
        assert store.list_conversations() == []

    def test_save_overwrites_existing(self):
        """Saving with same ID overwrites previous conversation."""
        store = InMemoryHistoryStore()
        conv1 = _make_conversation("c1", title="Original")
        store.save(conv1)
        conv2 = _make_conversation("c1", title="Updated")
        store.save(conv2)
        loaded = store.load("c1")
        assert loaded.title == "Updated"


# ────────────────────────────────────────────────────────────────────
# FileHistoryStore
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestFileHistoryStore:
    """Tests for FileHistoryStore (JSON-based file storage)."""

    def test_save_creates_json_file(self, tmp_path):
        """save creates a .json file for the conversation."""
        store = FileHistoryStore(str(tmp_path))
        conv = _make_conversation("file-conv-1")
        conv.add_user_message("hello")
        store.save(conv)
        expected_path = tmp_path / "file-conv-1.json"
        assert expected_path.exists()
        data = json.loads(expected_path.read_text())
        assert data["conversation_id"] == "file-conv-1"

    def test_save_and_load_roundtrip(self, tmp_path):
        """save then load restores conversation data."""
        store = FileHistoryStore(str(tmp_path))
        conv = _make_conversation("file-conv-2", title="File Test")
        conv.add_user_message("hello world")
        store.save(conv)
        loaded = store.load("file-conv-2")
        assert loaded is not None
        assert loaded.title == "File Test"
        assert len(loaded.messages) == 1
        assert loaded.messages[0].content == "hello world"

    def test_load_nonexistent_returns_none(self, tmp_path):
        """Loading missing conversation returns None."""
        store = FileHistoryStore(str(tmp_path))
        assert store.load("no-such-conv") is None

    def test_delete_existing(self, tmp_path):
        """Delete removes the JSON file."""
        store = FileHistoryStore(str(tmp_path))
        conv = _make_conversation("del-conv")
        store.save(conv)
        assert store.delete("del-conv") is True
        assert not (tmp_path / "del-conv.json").exists()

    def test_delete_nonexistent(self, tmp_path):
        """Delete of missing conversation returns False."""
        store = FileHistoryStore(str(tmp_path))
        assert store.delete("ghost") is False

    def test_list_conversations(self, tmp_path):
        """list_conversations finds all saved conversations."""
        store = FileHistoryStore(str(tmp_path))
        now = datetime.now()
        for i in range(3):
            c = _make_conversation(f"fc{i}", updated_at=now - timedelta(hours=i))
            store.save(c)
        result = store.list_conversations()
        assert len(result) == 3
        # Most recent first
        assert result[0].conversation_id == "fc0"

    def test_search_by_title(self, tmp_path):
        """search finds conversations by title match."""
        store = FileHistoryStore(str(tmp_path))
        store.save(_make_conversation("fc1", title="Bug Fix Session"))
        store.save(_make_conversation("fc2", title="Feature Design"))
        results = store.search("bug")
        assert len(results) == 1
        assert results[0].conversation_id == "fc1"

    def test_creates_directory_if_missing(self, tmp_path):
        """FileHistoryStore creates the directory on init."""
        new_dir = tmp_path / "subdir" / "history"
        store = FileHistoryStore(str(new_dir))
        assert new_dir.exists()


# ────────────────────────────────────────────────────────────────────
# SQLiteHistoryStore
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestSQLiteHistoryStore:
    """Tests for SQLiteHistoryStore."""

    def test_init_creates_tables(self, tmp_path):
        """Initialization creates conversations and messages tables."""
        import sqlite3
        db_path = str(tmp_path / "test.db")
        SQLiteHistoryStore(db_path)
        conn = sqlite3.connect(db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        table_names = {t[0] for t in tables}
        assert "conversations" in table_names
        assert "messages" in table_names

    def test_save_and_load(self, tmp_path):
        """save then load roundtrips a conversation."""
        db_path = str(tmp_path / "test.db")
        store = SQLiteHistoryStore(db_path)
        conv = _make_conversation("sql-conv-1", title="SQLite Test")
        conv.add_user_message("hello from sqlite")
        conv.add_assistant_message("hi back")
        store.save(conv)
        loaded = store.load("sql-conv-1")
        assert loaded is not None
        assert loaded.title == "SQLite Test"
        assert len(loaded.messages) == 2
        assert loaded.messages[0].content == "hello from sqlite"
        assert loaded.messages[1].content == "hi back"

    def test_load_nonexistent_returns_none(self, tmp_path):
        """Loading missing conversation returns None."""
        store = SQLiteHistoryStore(str(tmp_path / "test.db"))
        assert store.load("nope") is None

    def test_delete_existing(self, tmp_path):
        """Delete returns True and removes conversation."""
        store = SQLiteHistoryStore(str(tmp_path / "test.db"))
        conv = _make_conversation("sql-del")
        store.save(conv)
        assert store.delete("sql-del") is True
        assert store.load("sql-del") is None

    def test_delete_nonexistent(self, tmp_path):
        """Delete of missing conversation returns False."""
        store = SQLiteHistoryStore(str(tmp_path / "test.db"))
        assert store.delete("ghost") is False

    def test_list_conversations_ordered(self, tmp_path):
        """list_conversations returns most recent first."""
        store = SQLiteHistoryStore(str(tmp_path / "test.db"))
        now = datetime.now()
        for i in range(3):
            c = _make_conversation(f"sc{i}", updated_at=now - timedelta(hours=i))
            store.save(c)
        result = store.list_conversations(limit=10)
        ids = [c.conversation_id for c in result]
        assert ids == ["sc0", "sc1", "sc2"]

    def test_list_conversations_limit_and_offset(self, tmp_path):
        """list_conversations respects limit and offset."""
        store = SQLiteHistoryStore(str(tmp_path / "test.db"))
        now = datetime.now()
        for i in range(5):
            store.save(_make_conversation(f"sc{i}", updated_at=now - timedelta(hours=i)))
        result = store.list_conversations(limit=2, offset=1)
        assert len(result) == 2
        assert result[0].conversation_id == "sc1"

    def test_search_by_title(self, tmp_path):
        """search finds conversations matching title."""
        store = SQLiteHistoryStore(str(tmp_path / "test.db"))
        store.save(_make_conversation("sc1", title="Architecture Review"))
        store.save(_make_conversation("sc2", title="Daily Standup"))
        results = store.search("architecture")
        assert len(results) >= 1
        assert any(c.conversation_id == "sc1" for c in results)

    def test_search_by_message_content(self, tmp_path):
        """search finds conversations matching message content."""
        store = SQLiteHistoryStore(str(tmp_path / "test.db"))
        conv = _make_conversation(
            "sc-msg",
            title="General",
            messages=[(MessageRole.USER, "Fix the login timeout bug")],
        )
        store.save(conv)
        results = store.search("timeout")
        assert len(results) >= 1

    def test_save_overwrites_messages(self, tmp_path):
        """Re-saving updates messages correctly."""
        store = SQLiteHistoryStore(str(tmp_path / "test.db"))
        conv = _make_conversation("sc-overwrite")
        conv.add_user_message("first")
        store.save(conv)
        conv.add_assistant_message("second")
        store.save(conv)
        loaded = store.load("sc-overwrite")
        assert len(loaded.messages) == 2

    def test_message_metadata_preserved(self, tmp_path):
        """Message metadata survives save/load roundtrip."""
        store = SQLiteHistoryStore(str(tmp_path / "test.db"))
        conv = _make_conversation("sc-meta")
        conv.add_message(
            MessageRole.USER,
            "test content",
            tokens=55,
            metadata={"source": "cli"},
        )
        store.save(conv)
        loaded = store.load("sc-meta")
        assert loaded.messages[0].tokens == 55
        assert loaded.messages[0].metadata == {"source": "cli"}
