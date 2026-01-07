"""Tests for agent modularity and flexibility.

Tests use real implementations only. TestAgent is a test adapter
that implements BaseAgent interface for testing, not a mock.
"""

import pytest

from codomyrmex.agents.core import AgentRequest, AgentResponse, AgentCapabilities
from codomyrmex.agents.generic import BaseAgent, AgentOrchestrator
from codomyrmex.agents.opencode import OpenCodeClient, OpenCodeIntegrationAdapter
from codomyrmex.agents.jules import JulesClient, JulesIntegrationAdapter


class TestAgent(BaseAgent):
    """Test agent for testing modularity.
    
    This is a test adapter implementing BaseAgent interface, not a mock.
    """

    def __init__(self, name: str, capabilities: list[AgentCapabilities], should_succeed: bool = True):
        super().__init__(name=name, capabilities=capabilities, config={})
        self.should_succeed = should_succeed
        self.execution_count = 0

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        self.execution_count += 1
        if self.should_succeed:
            return AgentResponse(
                content=f"Response from {self.name}",
                metadata={"execution_count": self.execution_count}
            )
        else:
            return AgentResponse(content="", error=f"Error from {self.name}")

    def _stream_impl(self, request: AgentRequest):
        yield f"Stream from {self.name}"


class TestAgentSwapping:
    """Test agent swapping functionality."""

    def test_switching_between_agent_implementations(self):
        """Test switching between different agent implementations."""
        agent1 = TestAgent("agent1", [AgentCapabilities.CODE_GENERATION])
        agent2 = TestAgent("agent2", [AgentCapabilities.CODE_EDITING])
        
        request = AgentRequest(prompt="test")
        
        # Use agent1
        response1 = agent1.execute(request)
        assert response1.is_success()
        assert "agent1" in response1.content
        
        # Switch to agent2
        response2 = agent2.execute(request)
        assert response2.is_success()
        assert "agent2" in response2.content

    def test_hot_swapping_agents_in_orchestrator(self):
        """Test hot-swapping agents in orchestrator."""
        agent1 = TestAgent("agent1", [AgentCapabilities.CODE_GENERATION])
        agent2 = TestAgent("agent2", [AgentCapabilities.CODE_GENERATION])
        
        orchestrator = AgentOrchestrator([agent1])
        request = AgentRequest(prompt="test")
        
        # Execute with agent1
        responses1 = orchestrator.execute_parallel(request)
        assert len(responses1) == 1
        assert "agent1" in responses1[0].content
        
        # Hot-swap to agent2
        orchestrator.agents = [agent2]
        responses2 = orchestrator.execute_parallel(request)
        assert len(responses2) == 1
        assert "agent2" in responses2[0].content

    def test_agent_capability_discovery(self):
        """Test discovering agent capabilities."""
        agent1 = TestAgent("agent1", [
            AgentCapabilities.CODE_GENERATION,
            AgentCapabilities.CODE_EDITING
        ])
        agent2 = TestAgent("agent2", [
            AgentCapabilities.CODE_ANALYSIS,
            AgentCapabilities.TEXT_COMPLETION
        ])
        
        # Check capabilities
        assert agent1.supports_capability(AgentCapabilities.CODE_GENERATION)
        assert agent1.supports_capability(AgentCapabilities.CODE_EDITING)
        assert not agent1.supports_capability(AgentCapabilities.CODE_ANALYSIS)
        
        assert agent2.supports_capability(AgentCapabilities.CODE_ANALYSIS)
        assert not agent2.supports_capability(AgentCapabilities.CODE_GENERATION)

    def test_capability_based_selection(self):
        """Test selecting agents by capability."""
        agent1 = TestAgent("agent1", [AgentCapabilities.CODE_GENERATION])
        agent2 = TestAgent("agent2", [AgentCapabilities.CODE_EDITING])
        agent3 = TestAgent("agent3", [
            AgentCapabilities.CODE_GENERATION,
            AgentCapabilities.CODE_EDITING
        ])
        
        orchestrator = AgentOrchestrator([agent1, agent2, agent3])
        
        # Select agents with CODE_GENERATION
        code_gen_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_GENERATION.value
        )
        
        assert len(code_gen_agents) == 2
        assert agent1 in code_gen_agents
        assert agent3 in code_gen_agents
        assert agent2 not in code_gen_agents

    def test_multi_agent_coordination_different_capabilities(self):
        """Test coordinating multiple agents with different capabilities."""
        code_gen_agent = TestAgent("code_gen", [AgentCapabilities.CODE_GENERATION])
        code_edit_agent = TestAgent("code_edit", [AgentCapabilities.CODE_EDITING])
        analysis_agent = TestAgent("analysis", [AgentCapabilities.CODE_ANALYSIS])
        
        orchestrator = AgentOrchestrator([
            code_gen_agent,
            code_edit_agent,
            analysis_agent
        ])
        
        request = AgentRequest(prompt="test")
        responses = orchestrator.execute_parallel(request)
        
        assert len(responses) == 3
        assert all(r.is_success() for r in responses)
        
        # Verify each agent executed
        assert code_gen_agent.execution_count == 1
        assert code_edit_agent.execution_count == 1
        assert analysis_agent.execution_count == 1


class TestModularIntegration:
    """Test modular integration patterns."""

    def test_integration_adapter_pattern_verification(self):
        """Test that integration adapters work with different agents."""
        # Test with OpenCode
        opencode_client = OpenCodeClient()
        opencode_adapter = OpenCodeIntegrationAdapter(opencode_client)
        assert opencode_adapter.agent == opencode_client
        
        # Test with Jules
        jules_client = JulesClient()
        jules_adapter = JulesIntegrationAdapter(jules_client)
        assert jules_adapter.agent == jules_client

    def test_cross_agent_compatibility(self):
        """Test that different agents can work together."""
        agent1 = TestAgent("agent1", [AgentCapabilities.CODE_GENERATION])
        agent2 = TestAgent("agent2", [AgentCapabilities.CODE_GENERATION])
        
        orchestrator = AgentOrchestrator([agent1, agent2])
        request = AgentRequest(prompt="test")
        
        responses = orchestrator.execute_parallel(request)
        
        assert len(responses) == 2
        assert all(r.is_success() for r in responses)

    def test_plugin_style_agent_addition(self):
        """Test adding agents in plugin-style."""
        orchestrator = AgentOrchestrator([])
        
        # Add agents dynamically
        agent1 = TestAgent("agent1", [AgentCapabilities.CODE_GENERATION])
        orchestrator.agents.append(agent1)
        
        agent2 = TestAgent("agent2", [AgentCapabilities.CODE_EDITING])
        orchestrator.agents.append(agent2)
        
        assert len(orchestrator.agents) == 2
        
        request = AgentRequest(prompt="test")
        responses = orchestrator.execute_parallel(request)
        
        assert len(responses) == 2

    def test_agent_lifecycle_management(self):
        """Test agent lifecycle management."""
        agent1 = TestAgent("agent1", [AgentCapabilities.CODE_GENERATION])
        agent2 = TestAgent("agent2", [AgentCapabilities.CODE_GENERATION])
        
        orchestrator = AgentOrchestrator([agent1, agent2])
        
        # Execute
        request = AgentRequest(prompt="test")
        responses = orchestrator.execute_parallel(request)
        assert len(responses) == 2
        
        # Remove agent
        orchestrator.agents.remove(agent1)
        assert len(orchestrator.agents) == 1
        
        # Execute with remaining agent
        responses2 = orchestrator.execute_parallel(request)
        assert len(responses2) == 1
        assert "agent2" in responses2[0].content

    def test_mixed_agent_types_structure(self):
        """Test mixing different agent types structure."""
        test_agent = TestAgent("test", [AgentCapabilities.CODE_GENERATION])
        opencode_agent = OpenCodeClient()
        
        orchestrator = AgentOrchestrator([test_agent, opencode_agent])
        
        # Test structure without requiring execution
        assert len(orchestrator.agents) == 2
        assert orchestrator.agents[0] == test_agent
        assert orchestrator.agents[1] == opencode_agent

    def test_dynamic_capability_matching(self):
        """Test dynamic capability matching for agent selection."""
        agent1 = TestAgent("agent1", [AgentCapabilities.CODE_GENERATION])
        agent2 = TestAgent("agent2", [AgentCapabilities.CODE_EDITING])
        agent3 = TestAgent("agent3", [
            AgentCapabilities.CODE_GENERATION,
            AgentCapabilities.CODE_EDITING,
            AgentCapabilities.CODE_ANALYSIS
        ])
        
        orchestrator = AgentOrchestrator([agent1, agent2, agent3])
        
        # Request CODE_GENERATION capability
        code_gen_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_GENERATION.value
        )
        assert len(code_gen_agents) == 2
        assert agent1 in code_gen_agents
        assert agent3 in code_gen_agents
        
        # Request CODE_ANALYSIS capability
        analysis_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_ANALYSIS.value
        )
        assert len(analysis_agents) == 1
        assert agent3 in analysis_agents
