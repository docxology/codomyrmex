"""Integration tests for agents module."""

import pytest

from codomyrmex.agents.core import AgentRequest, AgentCapabilities


class TestAgentIntegrations:
    """Integration tests for agent framework integrations."""

    def test_agent_request_creation(self):
        """Test creating an agent request."""
        request = AgentRequest(
            prompt="Test prompt",
            capabilities=[AgentCapabilities.CODE_GENERATION]
        )
        assert request.prompt == "Test prompt"
        assert AgentCapabilities.CODE_GENERATION in request.capabilities

    def test_agent_response_structure(self):
        """Test agent response structure."""
        from codomyrmex.agents.core import AgentResponse

        response = AgentResponse(
            content="Test content",
            metadata={"test": "value"}
        )
        assert response.content == "Test content"
        assert response.is_success()
        assert response.metadata["test"] == "value"

