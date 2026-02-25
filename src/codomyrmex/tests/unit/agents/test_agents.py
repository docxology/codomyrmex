"""Tests for agents module."""

import pytest


class TestConversationOrchestrator:
    """Tests for ConversationOrchestrator."""

    def test_import(self):
        from codomyrmex.agents.orchestrator import ConversationOrchestrator
        assert ConversationOrchestrator is not None
