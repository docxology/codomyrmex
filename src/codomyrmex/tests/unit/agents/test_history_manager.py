"""Unit tests for codomyrmex.agents.history.manager module.

Tests ConversationManager: creation, save/load, search, active conversation, truncation.
"""

from __future__ import annotations


import pytest

from codomyrmex.agents.history.manager import ConversationManager
from codomyrmex.agents.history.models import Conversation, MessageRole
from codomyrmex.agents.history.stores import InMemoryHistoryStore


@pytest.mark.unit
class TestConversationManager:
    """Tests for the ConversationManager class."""

    def test_default_store(self):
        """Manager creates an InMemoryHistoryStore by default."""
        mgr = ConversationManager()
        assert isinstance(mgr.store, InMemoryHistoryStore)

    def test_custom_store(self):
        """Manager accepts a custom store."""
        store = InMemoryHistoryStore()
        mgr = ConversationManager(store=store)
        assert mgr.store is store

    def test_create_conversation_returns_conversation(self):
        """create_conversation returns a Conversation instance."""
        mgr = ConversationManager()
        conv = mgr.create_conversation("Test Session")
        assert isinstance(conv, Conversation)
        assert conv.title == "Test Session"
        assert len(conv.conversation_id) == 16

    def test_create_conversation_default_title(self):
        """create_conversation without title generates a default."""
        mgr = ConversationManager()
        conv = mgr.create_conversation()
        assert conv.title.startswith("Conversation ")

    def test_create_conversation_with_system_prompt(self):
        """create_conversation adds a system message when system_prompt is set."""
        mgr = ConversationManager()
        conv = mgr.create_conversation("SP Test", system_prompt="You are helpful")
        assert conv.message_count == 1
        assert conv.messages[0].role == MessageRole.SYSTEM
        assert conv.messages[0].content == "You are helpful"

    def test_create_sets_active(self):
        """create_conversation sets the active conversation."""
        mgr = ConversationManager()
        conv = mgr.create_conversation("Active Test")
        assert mgr.active is conv

    def test_save_and_get(self):
        """save persists conversation, get_conversation retrieves it."""
        mgr = ConversationManager()
        conv = mgr.create_conversation("Save Test")
        conv.add_user_message("hello")
        mgr.save(conv)
        loaded = mgr.get_conversation(conv.conversation_id)
        assert loaded is not None
        assert loaded.title == "Save Test"

    def test_save_active_when_no_arg(self):
        """save() with no argument saves the active conversation."""
        mgr = ConversationManager()
        conv = mgr.create_conversation("Auto Save")
        conv.add_user_message("data")
        mgr.save()
        loaded = mgr.get_conversation(conv.conversation_id)
        assert loaded is not None

    def test_save_truncates_when_over_limit(self):
        """save truncates messages exceeding max_messages_per_conversation."""
        mgr = ConversationManager(max_messages_per_conversation=3)
        conv = mgr.create_conversation("Truncate Test")
        for i in range(5):
            conv.add_user_message(f"msg-{i}")
        mgr.save(conv)
        loaded = mgr.get_conversation(conv.conversation_id)
        # Should have at most 3 non-system messages
        non_system = [m for m in loaded.messages if m.role != MessageRole.SYSTEM]
        assert len(non_system) <= 3

    def test_delete(self):
        """delete removes a conversation from the store."""
        mgr = ConversationManager()
        conv = mgr.create_conversation("Delete Test")
        mgr.save(conv)
        assert mgr.delete(conv.conversation_id) is True
        assert mgr.get_conversation(conv.conversation_id) is None

    def test_delete_nonexistent(self):
        """delete returns False for a missing conversation."""
        mgr = ConversationManager()
        assert mgr.delete("no-such-id") is False

    def test_list_recent(self):
        """list_recent returns saved conversations."""
        mgr = ConversationManager()
        c1 = mgr.create_conversation("First")
        mgr.save(c1)
        c2 = mgr.create_conversation("Second")
        mgr.save(c2)
        recents = mgr.list_recent(limit=10)
        assert len(recents) == 2

    def test_search(self):
        """search delegates to the store's search."""
        mgr = ConversationManager()
        c1 = mgr.create_conversation("Bug Triage")
        c1.add_user_message("The auth module is broken")
        mgr.save(c1)
        c2 = mgr.create_conversation("Feature Planning")
        mgr.save(c2)
        results = mgr.search("auth")
        assert len(results) >= 1
        assert any(c.conversation_id == c1.conversation_id for c in results)

    def test_set_active(self):
        """set_active loads and sets a conversation as active."""
        mgr = ConversationManager()
        conv = mgr.create_conversation("Set Active")
        mgr.save(conv)
        # Create a new conversation (shifts active)
        mgr.create_conversation("Other")
        assert mgr.active.title == "Other"
        # set_active restores the first conversation
        result = mgr.set_active(conv.conversation_id)
        assert result is not None
        assert mgr.active.conversation_id == conv.conversation_id

    def test_set_active_nonexistent_returns_none(self):
        """set_active returns None if conversation not found."""
        mgr = ConversationManager()
        result = mgr.set_active("ghost-id")
        assert result is None

    def test_metadata_on_create(self):
        """create_conversation passes extra kwargs as metadata."""
        mgr = ConversationManager()
        conv = mgr.create_conversation("Meta", agent="engineer", priority="high")
        assert conv.metadata["agent"] == "engineer"
        assert conv.metadata["priority"] == "high"
