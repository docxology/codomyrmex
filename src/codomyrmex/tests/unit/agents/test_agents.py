"""Tests for agents module."""



class TestConversationOrchestrator:
    """Tests for ConversationOrchestrator."""

    def test_import(self):
        from codomyrmex.agents.orchestrator import ConversationOrchestrator
        assert ConversationOrchestrator is not None
