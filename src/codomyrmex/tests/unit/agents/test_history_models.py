"""Unit tests for codomyrmex.agents.history.models module.

Tests MessageRole enum, HistoryMessage dataclass, and Conversation dataclass.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from codomyrmex.agents.history.models import (
    Conversation,
    HistoryMessage,
    MessageRole,
)


@pytest.mark.unit
class TestMessageRole:
    """Tests for the MessageRole enum."""

    def test_all_roles_defined(self):
        """All expected roles exist."""
        assert MessageRole.SYSTEM.value == "system"
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.TOOL.value == "tool"
        assert MessageRole.FUNCTION.value == "function"

    def test_role_count(self):
        """Five roles are defined."""
        assert len(MessageRole) == 5

    def test_role_from_value(self):
        """Can construct MessageRole from string value."""
        assert MessageRole("user") == MessageRole.USER
        assert MessageRole("assistant") == MessageRole.ASSISTANT


@pytest.mark.unit
class TestHistoryMessage:
    """Tests for the HistoryMessage dataclass."""

    def test_basic_creation(self):
        """HistoryMessage can be created with role and content."""
        msg = HistoryMessage(role=MessageRole.USER, content="Hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"
        assert msg.tokens == 0
        assert isinstance(msg.timestamp, datetime)
        assert msg.message_id is not None

    def test_auto_generated_id_is_hex_string(self):
        """Auto-generated message_id is a 16-char hex string."""
        msg = HistoryMessage(role=MessageRole.USER, content="test")
        assert len(msg.message_id) == 16
        int(msg.message_id, 16)  # should not raise

    def test_explicit_message_id(self):
        """Explicit message_id is preserved."""
        msg = HistoryMessage(
            role=MessageRole.ASSISTANT,
            content="answer",
            message_id="custom-id-123",
        )
        assert msg.message_id == "custom-id-123"

    def test_metadata_defaults_to_empty_dict(self):
        """Metadata defaults to empty dict."""
        msg = HistoryMessage(role=MessageRole.SYSTEM, content="init")
        assert msg.metadata == {}

    def test_to_dict(self):
        """to_dict produces expected keys."""
        ts = datetime(2025, 1, 15, 12, 0, 0)
        msg = HistoryMessage(
            role=MessageRole.USER,
            content="query",
            timestamp=ts,
            message_id="abc123",
            tokens=42,
            metadata={"source": "cli"},
        )
        d = msg.to_dict()
        assert d["role"] == "user"
        assert d["content"] == "query"
        assert d["message_id"] == "abc123"
        assert d["timestamp"] == "2025-01-15T12:00:00"
        assert d["tokens"] == 42
        assert d["metadata"] == {"source": "cli"}

    def test_from_dict_roundtrip(self):
        """from_dict restores a message from its to_dict output."""
        original = HistoryMessage(
            role=MessageRole.ASSISTANT,
            content="response text",
            tokens=100,
            metadata={"model": "gpt-4"},
        )
        d = original.to_dict()
        restored = HistoryMessage.from_dict(d)
        assert restored.role == original.role
        assert restored.content == original.content
        assert restored.tokens == original.tokens
        assert restored.metadata == original.metadata
        assert restored.message_id == original.message_id

    def test_from_dict_minimal(self):
        """from_dict works with minimal required fields."""
        d = {
            "role": "user",
            "content": "hello",
            "timestamp": "2025-06-01T10:00:00",
        }
        msg = HistoryMessage.from_dict(d)
        assert msg.role == MessageRole.USER
        assert msg.content == "hello"
        assert msg.tokens == 0
        assert msg.metadata == {}


@pytest.mark.unit
class TestConversation:
    """Tests for the Conversation dataclass."""

    def test_basic_creation(self):
        """Conversation can be created with minimal args."""
        conv = Conversation(conversation_id="conv-001", title="Test")
        assert conv.conversation_id == "conv-001"
        assert conv.title == "Test"
        assert conv.messages == []
        assert isinstance(conv.created_at, datetime)
        assert isinstance(conv.updated_at, datetime)

    def test_add_message(self):
        """add_message appends a message and updates updated_at."""
        conv = Conversation(conversation_id="c1", title="t1")
        before = conv.updated_at
        msg = conv.add_message(MessageRole.USER, "hello")
        assert isinstance(msg, HistoryMessage)
        assert msg.role == MessageRole.USER
        assert msg.content == "hello"
        assert len(conv.messages) == 1
        assert conv.updated_at >= before

    def test_add_user_message(self):
        """add_user_message is a convenience for USER role."""
        conv = Conversation(conversation_id="c2")
        msg = conv.add_user_message("question")
        assert msg.role == MessageRole.USER
        assert msg.content == "question"

    def test_add_assistant_message(self):
        """add_assistant_message is a convenience for ASSISTANT role."""
        conv = Conversation(conversation_id="c3")
        msg = conv.add_assistant_message("answer")
        assert msg.role == MessageRole.ASSISTANT
        assert msg.content == "answer"

    def test_message_count(self):
        """message_count property reflects the number of messages."""
        conv = Conversation(conversation_id="c4")
        assert conv.message_count == 0
        conv.add_user_message("a")
        conv.add_assistant_message("b")
        assert conv.message_count == 2

    def test_total_tokens(self):
        """total_tokens sums tokens across all messages."""
        conv = Conversation(conversation_id="c5")
        conv.add_message(MessageRole.USER, "x", tokens=50)
        conv.add_message(MessageRole.ASSISTANT, "y", tokens=100)
        assert conv.total_tokens == 150

    def test_get_messages_for_api(self):
        """get_messages_for_api returns API-compatible dicts."""
        conv = Conversation(conversation_id="c6")
        conv.add_message(MessageRole.SYSTEM, "You are helpful")
        conv.add_user_message("hi")
        msgs = conv.get_messages_for_api()
        assert len(msgs) == 2
        assert msgs[0] == {"role": "system", "content": "You are helpful"}
        assert msgs[1] == {"role": "user", "content": "hi"}

    def test_get_messages_for_api_exclude_system(self):
        """get_messages_for_api with include_system=False filters system messages."""
        conv = Conversation(conversation_id="c7")
        conv.add_message(MessageRole.SYSTEM, "system prompt")
        conv.add_user_message("question")
        msgs = conv.get_messages_for_api(include_system=False)
        assert len(msgs) == 1
        assert msgs[0]["role"] == "user"

    def test_truncate_removes_oldest_non_system(self):
        """truncate keeps system messages and most recent non-system messages."""
        conv = Conversation(conversation_id="c8")
        conv.add_message(MessageRole.SYSTEM, "sys")
        for i in range(5):
            conv.add_user_message(f"msg-{i}")
        removed = conv.truncate(3)
        assert len(removed) == 2
        assert removed[0].content == "msg-0"
        assert removed[1].content == "msg-1"
        # system + 3 most recent
        assert len(conv.messages) == 4
        assert conv.messages[0].role == MessageRole.SYSTEM

    def test_truncate_no_op_when_under_limit(self):
        """truncate returns empty list when already under limit."""
        conv = Conversation(conversation_id="c9")
        conv.add_user_message("a")
        removed = conv.truncate(10)
        assert removed == []
        assert conv.message_count == 1

    def test_to_dict_and_from_dict_roundtrip(self):
        """Conversation survives to_dict/from_dict roundtrip."""
        conv = Conversation(conversation_id="c10", title="Roundtrip Test")
        conv.add_user_message("hello")
        conv.add_assistant_message("world")
        d = conv.to_dict()
        restored = Conversation.from_dict(d)
        assert restored.conversation_id == "c10"
        assert restored.title == "Roundtrip Test"
        assert len(restored.messages) == 2
        assert restored.messages[0].content == "hello"
        assert restored.messages[1].content == "world"
