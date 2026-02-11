"""Tests for agent history: HistoryMessage, Conversation, InMemoryHistoryStore, FileHistoryStore, SQLiteHistoryStore, ConversationManager."""

import os
import tempfile

import pytest

from codomyrmex.agents.history import (
    Conversation,
    ConversationManager,
    FileHistoryStore,
    HistoryMessage,
    InMemoryHistoryStore,
    MessageRole,
    SQLiteHistoryStore,
)


# ── HistoryMessage ────────────────────────────────────────────────────────


class TestHistoryMessage:
    def test_creation(self):
        msg = HistoryMessage(role=MessageRole.USER, content="hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "hello"
        assert msg.message_id is not None

    def test_serialization_roundtrip(self):
        msg = HistoryMessage(role=MessageRole.ASSISTANT, content="answer", tokens=42)
        d = msg.to_dict()
        restored = HistoryMessage.from_dict(d)
        assert restored.role == msg.role
        assert restored.content == msg.content
        assert restored.tokens == 42


# ── Conversation ──────────────────────────────────────────────────────────


class TestConversation:
    def test_add_messages(self):
        conv = Conversation(conversation_id="c1")
        conv.add_user_message("hi")
        conv.add_assistant_message("hello")
        assert conv.message_count == 2

    def test_api_format(self):
        conv = Conversation(conversation_id="c2")
        conv.add_message(MessageRole.SYSTEM, "you are helpful")
        conv.add_user_message("q")
        fmt = conv.get_messages_for_api()
        assert len(fmt) == 2
        assert fmt[0]["role"] == "system"

    def test_api_format_no_system(self):
        conv = Conversation(conversation_id="c2b")
        conv.add_message(MessageRole.SYSTEM, "sys")
        conv.add_user_message("q")
        fmt = conv.get_messages_for_api(include_system=False)
        assert all(m["role"] != "system" for m in fmt)

    def test_truncate_preserves_system(self):
        conv = Conversation(conversation_id="c3")
        conv.add_message(MessageRole.SYSTEM, "system msg")
        for i in range(10):
            conv.add_user_message(f"msg {i}")
        removed = conv.truncate(max_messages=5)
        assert len(removed) > 0
        roles = [m.role for m in conv.messages]
        assert MessageRole.SYSTEM in roles

    def test_total_tokens(self):
        conv = Conversation(conversation_id="c4")
        conv.add_message(MessageRole.USER, "a", tokens=10)
        conv.add_message(MessageRole.ASSISTANT, "b", tokens=20)
        assert conv.total_tokens == 30

    def test_serialization_roundtrip(self):
        conv = Conversation(conversation_id="c5", title="Test")
        conv.add_user_message("hello")
        d = conv.to_dict()
        restored = Conversation.from_dict(d)
        assert restored.conversation_id == "c5"
        assert restored.message_count == 1


# ── InMemoryHistoryStore ──────────────────────────────────────────────────


class TestInMemoryHistoryStore:
    def test_crud(self):
        store = InMemoryHistoryStore()
        conv = Conversation(conversation_id="m1", title="Memory Test")
        conv.add_user_message("hi")
        store.save(conv)
        loaded = store.load("m1")
        assert loaded.title == "Memory Test"
        store.delete("m1")
        assert store.load("m1") is None

    def test_list_conversations(self):
        store = InMemoryHistoryStore()
        for i in range(5):
            store.save(Conversation(conversation_id=f"lc{i}"))
        listed = store.list_conversations(limit=3)
        assert len(listed) == 3

    def test_search(self):
        store = InMemoryHistoryStore()
        c = Conversation(conversation_id="s1")
        c.add_user_message("unique_token_xyz")
        store.save(c)
        found = store.search("unique_token_xyz")
        assert len(found) >= 1

    def test_clear(self):
        store = InMemoryHistoryStore()
        store.save(Conversation(conversation_id="cl1"))
        store.clear()
        assert store.list_conversations() == []


# ── FileHistoryStore ──────────────────────────────────────────────────────


class TestFileHistoryStore:
    def test_save_load(self, tmp_path):
        store = FileHistoryStore(str(tmp_path))
        conv = Conversation(conversation_id="f1", title="File Test")
        conv.add_user_message("persisted")
        store.save(conv)
        loaded = store.load("f1")
        assert loaded is not None
        assert loaded.title == "File Test"
        assert loaded.message_count == 1

    def test_delete(self, tmp_path):
        store = FileHistoryStore(str(tmp_path))
        store.save(Conversation(conversation_id="fd1"))
        store.delete("fd1")
        assert store.load("fd1") is None

    def test_list(self, tmp_path):
        store = FileHistoryStore(str(tmp_path))
        for i in range(3):
            store.save(Conversation(conversation_id=f"fl{i}"))
        listed = store.list_conversations()
        assert len(listed) == 3


# ── SQLiteHistoryStore ────────────────────────────────────────────────────


class TestSQLiteHistoryStore:
    def test_save_load(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = SQLiteHistoryStore(db_path)
        conv = Conversation(conversation_id="sq1", title="SQLite Test")
        conv.add_user_message("hello sqlite")
        store.save(conv)
        loaded = store.load("sq1")
        assert loaded is not None
        assert loaded.title == "SQLite Test"
        assert loaded.message_count == 1

    def test_delete(self, tmp_path):
        db_path = str(tmp_path / "del.db")
        store = SQLiteHistoryStore(db_path)
        store.save(Conversation(conversation_id="sd1"))
        store.delete("sd1")
        assert store.load("sd1") is None

    def test_search(self, tmp_path):
        db_path = str(tmp_path / "search.db")
        store = SQLiteHistoryStore(db_path)
        c = Conversation(conversation_id="ss1")
        c.add_user_message("searchable_keyword_abc")
        store.save(c)
        found = store.search("searchable_keyword_abc")
        assert len(found) >= 1


# ── ConversationManager ──────────────────────────────────────────────────


class TestConversationManager:
    def test_create_and_active(self):
        mgr = ConversationManager()
        conv = mgr.create_conversation(title="Test Session")
        assert conv.title == "Test Session"
        assert mgr.active is not None
        assert mgr.active.conversation_id == conv.conversation_id

    def test_set_active(self):
        mgr = ConversationManager()
        c1 = mgr.create_conversation(title="A")
        mgr.save(c1)  # persist to store
        c2 = mgr.create_conversation(title="B")
        mgr.save(c2)  # persist to store
        mgr.set_active(c1.conversation_id)
        assert mgr.active.conversation_id == c1.conversation_id

    def test_list_recent(self):
        mgr = ConversationManager()
        for i in range(5):
            conv = mgr.create_conversation(title=f"Conv {i}")
            mgr.save(conv)  # persist to store
        recent = mgr.list_recent(limit=3)
        assert len(recent) == 3
