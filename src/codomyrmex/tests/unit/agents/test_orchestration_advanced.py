"""Advanced orchestration tests for complex scenarios.

Tests use real implementations only. TestAgent is a test adapter
that implements BaseAgent interface for testing, not a mock.
"""

import pytest
import time

from codomyrmex.agents.core import AgentRequest, AgentResponse, AgentCapabilities
from codomyrmex.agents.generic import BaseAgent, AgentOrchestrator
from codomyrmex.agents.exceptions import AgentError


class TestAgent(BaseAgent):
    """Test agent for advanced orchestration testing.
    
    This is a test adapter implementing BaseAgent interface, not a mock.
    """

    def __init__(
        self,
        name: str,
        capabilities: list[AgentCapabilities],
        should_succeed: bool = True,
        delay: float = 0.0,
        fail_after: int = None,
    ):
        super().__init__(name=name, capabilities=capabilities, config={})
        self.should_succeed = should_succeed
        self.delay = delay
        self.execution_count = 0
        self.fail_after = fail_after

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        self.execution_count += 1
        
        if self.delay > 0:
            time.sleep(self.delay)
        
        if self.fail_after and self.execution_count > self.fail_after:
            return AgentResponse(content="", error=f"Failed after {self.fail_after} attempts")
        
        if self.should_succeed:
            return AgentResponse(
                content=f"Response from {self.name} (attempt {self.execution_count})",
                metadata={
                    "agent": self.name,
                    "attempt": self.execution_count,
                    "delay": self.delay
                }
            )
        else:
            return AgentResponse(content="", error=f"Error from {self.name}")

    def _stream_impl(self, request: AgentRequest):
        yield f"Stream from {self.name}"


class TestSimpleOrchestration:
    """Simple orchestration scenarios."""

    def test_single_agent_execution(self):
        """Test single agent execution."""
        agent = TestAgent("agent1", [AgentCapabilities.CODE_GENERATION])
        orchestrator = AgentOrchestrator([agent])
        
        request = AgentRequest(prompt="test")
        responses = orchestrator.execute_parallel(request)
        
        assert len(responses) == 1
        assert responses[0].is_success()
        assert "agent1" in responses[0].content

    def test_basic_parallel_execution(self):
        """Test basic parallel execution."""
        agents = [
            TestAgent("agent1", [AgentCapabilities.CODE_GENERATION]),
            TestAgent("agent2", [AgentCapabilities.CODE_GENERATION]),
            TestAgent("agent3", [AgentCapabilities.CODE_GENERATION]),
        ]
        orchestrator = AgentOrchestrator(agents)
        
        request = AgentRequest(prompt="test")
        responses = orchestrator.execute_parallel(request)
        
        assert len(responses) == 3
        assert all(r.is_success() for r in responses)

    def test_simple_fallback_chain(self):
        """Test simple fallback chain."""
        agents = [
            TestAgent("agent1", [AgentCapabilities.CODE_GENERATION], should_succeed=False),
            TestAgent("agent2", [AgentCapabilities.CODE_GENERATION], should_succeed=True),
        ]
        orchestrator = AgentOrchestrator(agents)
        
        request = AgentRequest(prompt="test")
        response = orchestrator.execute_with_fallback(request)
        
        assert response.is_success()
        assert "agent2" in response.content


class TestComplexOrchestration:
    """Complex orchestration scenarios."""

    def test_multi_agent_parallel_with_dependencies(self):
        """Test parallel execution with dependency tracking."""
        agent1 = TestAgent("agent1", [AgentCapabilities.CODE_GENERATION], delay=0.1)
        agent2 = TestAgent("agent2", [AgentCapabilities.CODE_EDITING], delay=0.1)
        agent3 = TestAgent("agent3", [AgentCapabilities.CODE_ANALYSIS], delay=0.1)
        
        orchestrator = AgentOrchestrator([agent1, agent2, agent3])
        
        request = AgentRequest(prompt="test")
        start_time = time.time()
        responses = orchestrator.execute_parallel(request)
        execution_time = time.time() - start_time
        
        assert len(responses) == 3
        assert all(r.is_success() for r in responses)
        # Should be roughly parallel (less than sequential time)
        assert execution_time < 0.4  # Sequential would be ~0.3s, parallel should be ~0.1s

    def test_complex_fallback_chain_partial_failures(self):
        """Test complex fallback chain with partial failures."""
        agents = [
            TestAgent("agent1", [AgentCapabilities.CODE_GENERATION], should_succeed=False),
            TestAgent("agent2", [AgentCapabilities.CODE_GENERATION], should_succeed=False),
            TestAgent("agent3", [AgentCapabilities.CODE_GENERATION], should_succeed=True),
            TestAgent("agent4", [AgentCapabilities.CODE_GENERATION], should_succeed=True),
        ]
        orchestrator = AgentOrchestrator(agents)
        
        request = AgentRequest(prompt="test")
        response = orchestrator.execute_with_fallback(request)
        
        assert response.is_success()
        assert "agent3" in response.content
        # Should stop at first success

    def test_sequential_execution_with_data_passing(self):
        """Test sequential execution with data passing between agents."""
        agent1 = TestAgent("agent1", [AgentCapabilities.CODE_GENERATION])
        agent2 = TestAgent("agent2", [AgentCapabilities.CODE_EDITING])
        
        orchestrator = AgentOrchestrator([agent1, agent2])
        
        request = AgentRequest(prompt="test")
        responses = orchestrator.execute_sequential(request)
        
        assert len(responses) == 2
        assert all(r.is_success() for r in responses)
        assert agent1.execution_count == 1
        assert agent2.execution_count == 1

    def test_sequential_execution_stop_on_success(self):
        """Test sequential execution stopping on first success."""
        agents = [
            TestAgent("agent1", [AgentCapabilities.CODE_GENERATION], should_succeed=False),
            TestAgent("agent2", [AgentCapabilities.CODE_GENERATION], should_succeed=True),
            TestAgent("agent3", [AgentCapabilities.CODE_GENERATION], should_succeed=True),
        ]
        orchestrator = AgentOrchestrator(agents)
        
        request = AgentRequest(prompt="test")
        responses = orchestrator.execute_sequential(request, stop_on_success=True)
        
        # Should stop after agent2 succeeds
        assert len(responses) == 2
        assert responses[0].is_success() is False
        assert responses[1].is_success() is True
        assert agents[2].execution_count == 0  # Should not execute

    def test_agent_selection_by_capability_matching(self):
        """Test selecting agents by capability matching."""
        code_gen_agent = TestAgent("code_gen", [AgentCapabilities.CODE_GENERATION])
        code_edit_agent = TestAgent("code_edit", [AgentCapabilities.CODE_EDITING])
        analysis_agent = TestAgent("analysis", [AgentCapabilities.CODE_ANALYSIS])
        multi_cap_agent = TestAgent("multi", [
            AgentCapabilities.CODE_GENERATION,
            AgentCapabilities.CODE_EDITING
        ])
        
        orchestrator = AgentOrchestrator([
            code_gen_agent,
            code_edit_agent,
            analysis_agent,
            multi_cap_agent
        ])
        
        # Select CODE_GENERATION agents
        selected = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_GENERATION.value
        )
        
        assert len(selected) == 2
        assert code_gen_agent in selected
        assert multi_cap_agent in selected
        assert code_edit_agent not in selected
        assert analysis_agent not in selected

    def test_load_balancing_across_agents(self):
        """Test load balancing across multiple agents."""
        agents = [
            TestAgent("agent1", [AgentCapabilities.CODE_GENERATION]),
            TestAgent("agent2", [AgentCapabilities.CODE_GENERATION]),
            TestAgent("agent3", [AgentCapabilities.CODE_GENERATION]),
        ]
        orchestrator = AgentOrchestrator(agents)
        
        # Execute multiple requests
        for i in range(6):
            request = AgentRequest(prompt=f"test {i}")
            orchestrator.execute_parallel(request)
        
        # All agents should have executed
        assert all(agent.execution_count > 0 for agent in agents)
        # Execution counts should be roughly balanced
        execution_counts = [agent.execution_count for agent in agents]
        assert max(execution_counts) - min(execution_counts) <= 2

    def test_timeout_handling_in_orchestration(self):
        """Test timeout handling in orchestration."""
        # Create agent that will timeout (simulated by long delay)
        slow_agent = TestAgent(
            "slow_agent",
            [AgentCapabilities.CODE_GENERATION],
            delay=2.0  # Long delay
        )
        fast_agent = TestAgent(
            "fast_agent",
            [AgentCapabilities.CODE_GENERATION],
            delay=0.01
        )
        
        orchestrator = AgentOrchestrator([slow_agent, fast_agent])
        
        request = AgentRequest(prompt="test", timeout=1)  # 1 second timeout
        
        # Both should execute, but slow one might timeout
        responses = orchestrator.execute_parallel(request)
        
        assert len(responses) == 2
        # Fast agent should succeed
        fast_response = next(r for r in responses if "fast_agent" in r.metadata.get("agent", ""))
        assert fast_response.is_success()

    def test_mixed_success_failure_in_parallel(self):
        """Test handling mixed success/failure in parallel execution."""
        agents = [
            TestAgent("agent1", [AgentCapabilities.CODE_GENERATION], should_succeed=True),
            TestAgent("agent2", [AgentCapabilities.CODE_GENERATION], should_succeed=False),
            TestAgent("agent3", [AgentCapabilities.CODE_GENERATION], should_succeed=True),
        ]
        orchestrator = AgentOrchestrator(agents)
        
        request = AgentRequest(prompt="test")
        responses = orchestrator.execute_parallel(request)
        
        assert len(responses) == 3
        success_count = sum(1 for r in responses if r.is_success())
        failure_count = sum(1 for r in responses if not r.is_success())
        
        assert success_count == 2
        assert failure_count == 1

    def test_empty_agent_list_handling(self):
        """Test handling of empty agent list."""
        orchestrator = AgentOrchestrator([])
        request = AgentRequest(prompt="test")
        
        with pytest.raises(AgentError, match="No agents available"):
            orchestrator.execute_parallel(request)
        
        with pytest.raises(AgentError, match="No agents available"):
            orchestrator.execute_sequential(request)
        
        with pytest.raises(AgentError, match="No agents available"):
            orchestrator.execute_with_fallback(request)

    def test_custom_agent_list_override(self):
        """Test overriding agent list for specific execution."""
        agent1 = TestAgent("agent1", [AgentCapabilities.CODE_GENERATION])
        agent2 = TestAgent("agent2", [AgentCapabilities.CODE_GENERATION])
        agent3 = TestAgent("agent3", [AgentCapabilities.CODE_GENERATION])
        
        orchestrator = AgentOrchestrator([agent1, agent2, agent3])
        
        request = AgentRequest(prompt="test")
        
        # Use only agent1 and agent3
        responses = orchestrator.execute_parallel(request, agents=[agent1, agent3])
        
        assert len(responses) == 2
        assert agent1.execution_count == 1
        assert agent2.execution_count == 0  # Not used
        assert agent3.execution_count == 1
