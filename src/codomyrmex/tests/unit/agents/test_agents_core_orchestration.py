
import pytest
from codomyrmex.agents.core import AgentCapabilities, AgentError
from codomyrmex.agents.generic.agent_orchestrator import AgentOrchestrator
from codomyrmex.tests.unit.agents.conftest import ConcreteAgent, FailingAgent

class TestAgentOrchestrator:
    """Test multi-agent orchestration."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization with agents."""
        agents = [ConcreteAgent("agent1"), ConcreteAgent("agent2")]
        orchestrator = AgentOrchestrator(agents)
        assert len(orchestrator.agents) == 2

    def test_execute_parallel(self, sample_agent_request):
        """Test parallel execution on multiple agents."""
        agents = [
            ConcreteAgent("agent1"),
            ConcreteAgent("agent2"),
            ConcreteAgent("agent3"),
        ]
        orchestrator = AgentOrchestrator(agents)

        responses = orchestrator.execute_parallel(sample_agent_request)
        assert len(responses) == 3
        assert all(r.is_success() for r in responses)

    def test_execute_parallel_with_failure(self, sample_agent_request):
        """Test parallel execution handles agent failures."""
        agents = [
            ConcreteAgent("agent1"),
            FailingAgent("Agent failed"),
            ConcreteAgent("agent3"),
        ]
        orchestrator = AgentOrchestrator(agents)

        responses = orchestrator.execute_parallel(sample_agent_request)
        assert len(responses) == 3
        success_count = sum(1 for r in responses if r.is_success())
        assert success_count == 2

    def test_execute_sequential(self, sample_agent_request):
        """Test sequential execution on multiple agents."""
        agents = [ConcreteAgent("agent1"), ConcreteAgent("agent2")]
        orchestrator = AgentOrchestrator(agents)

        responses = orchestrator.execute_sequential(sample_agent_request)
        assert len(responses) == 2

    def test_execute_sequential_stop_on_success(self, sample_agent_request):
        """Test sequential execution stops on first success."""
        agents = [ConcreteAgent("agent1"), ConcreteAgent("agent2")]
        orchestrator = AgentOrchestrator(agents)

        responses = orchestrator.execute_sequential(
            sample_agent_request, stop_on_success=True
        )
        assert len(responses) == 1

    def test_execute_with_fallback(self, sample_agent_request):
        """Test fallback execution."""
        agents = [
            FailingAgent("First failed"),
            FailingAgent("Second failed"),
            ConcreteAgent("success"),
        ]
        orchestrator = AgentOrchestrator(agents)

        response = orchestrator.execute_with_fallback(sample_agent_request)
        assert response.is_success()
        assert "Default test response" in response.content

    def test_execute_with_fallback_all_fail(self, sample_agent_request):
        """Test fallback when all agents fail."""
        agents = [
            FailingAgent("First failed"),
            FailingAgent("Second failed"),
        ]
        orchestrator = AgentOrchestrator(agents)

        response = orchestrator.execute_with_fallback(sample_agent_request)
        assert not response.is_success()

    def test_execute_no_agents_raises(self, sample_agent_request):
        """Test orchestrator raises when no agents available."""
        orchestrator = AgentOrchestrator([])

        with pytest.raises(AgentError):
            orchestrator.execute_parallel(sample_agent_request)

    def test_select_agent_by_capability(self):
        """Test selecting agents by capability."""
        agent1 = ConcreteAgent(
            "vision_agent",
            capabilities=[AgentCapabilities.VISION, AgentCapabilities.TEXT_COMPLETION],
        )
        agent2 = ConcreteAgent(
            "text_agent", capabilities=[AgentCapabilities.TEXT_COMPLETION]
        )
        orchestrator = AgentOrchestrator([agent1, agent2])

        vision_agents = orchestrator.select_agent_by_capability("vision")
        assert len(vision_agents) == 1
        assert vision_agents[0].name == "vision_agent"
