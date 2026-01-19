"""Tests for agent orchestration."""

import pytest

from codomyrmex.agents.core import AgentRequest, AgentResponse, AgentCapabilities
from codomyrmex.agents.core import BaseAgent
from codomyrmex.agents.generic.agent_orchestrator import AgentOrchestrator


class MockAgent(BaseAgent):
    """Mock agent for testing."""

    def __init__(self, name: str, should_succeed: bool = True):
        super().__init__(
            name=name,
            capabilities=[AgentCapabilities.CODE_GENERATION],
            config={}
        )
        self.should_succeed = should_succeed

    def _execute_impl(self, request):
        if self.should_succeed:
            return AgentResponse(content=f"Response from {self.name}")
        else:
            return AgentResponse(content="", error="Mock error")


class TestAgentOrchestration:
    """Tests for agent orchestration."""

    def test_parallel_execution(self):
        """Test parallel agent execution."""
        agents = [
            MockAgent("agent1"),
            MockAgent("agent2"),
            MockAgent("agent3")
        ]
        orchestrator = AgentOrchestrator(agents)

        request = AgentRequest(prompt="Test")
        responses = orchestrator.execute_parallel(request)

        assert len(responses) == 3
        assert all(r.is_success() for r in responses)

    def test_sequential_execution(self):
        """Test sequential agent execution."""
        agents = [
            MockAgent("agent1"),
            MockAgent("agent2")
        ]
        orchestrator = AgentOrchestrator(agents)

        request = AgentRequest(prompt="Test")
        responses = orchestrator.execute_sequential(request)

        assert len(responses) == 2

    def test_fallback_execution(self):
        """Test fallback execution."""
        agents = [
            MockAgent("agent1", should_succeed=False),
            MockAgent("agent2", should_succeed=True)
        ]
        orchestrator = AgentOrchestrator(agents)

        request = AgentRequest(prompt="Test")
        response = orchestrator.execute_with_fallback(request)

        assert response.is_success()
        assert "agent2" in response.content

