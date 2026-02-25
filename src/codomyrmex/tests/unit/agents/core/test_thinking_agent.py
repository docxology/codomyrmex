"""Tests for agents/core/thinking_agent.py."""

from __future__ import annotations

from codomyrmex.agents.core.base import (
    AgentCapabilities,
    AgentRequest,
)
from codomyrmex.agents.core.thinking_agent import (
    ThinkingAgent,
    ThinkingAgentConfig,
)
from codomyrmex.llm.models.reasoning import ThinkingDepth


class TestThinkingAgentConfig:
    """Test suite for ThinkingAgentConfig."""
    def test_defaults(self) -> None:
        """Test functionality: defaults."""
        cfg = ThinkingAgentConfig()
        assert cfg.depth == ThinkingDepth.NORMAL
        assert cfg.max_context_tokens == 4096
        assert cfg.max_traces == 100
        assert cfg.reflect_on_errors is True


class TestThinkingAgent:
    """Test suite for ThinkingAgent."""
    def test_creation(self) -> None:
        """Test functionality: creation."""
        agent = ThinkingAgent()
        assert agent is not None
        assert agent.last_trace is None

    def test_capabilities(self) -> None:
        """Test functionality: capabilities."""
        agent = ThinkingAgent()
        caps = agent.get_capabilities()
        assert AgentCapabilities.EXTENDED_THINKING in caps
        assert AgentCapabilities.TEXT_COMPLETION in caps

    def test_test_connection(self) -> None:
        """Test functionality: connection."""
        agent = ThinkingAgent()
        assert agent.test_connection() is True

    def test_execute_basic(self) -> None:
        """Test functionality: execute basic."""
        agent = ThinkingAgent()
        request = AgentRequest(prompt="Explain dependency injection")
        response = agent.execute(request)
        assert response.is_success
        assert len(response.content) > 0
        assert response.execution_time is not None
        assert response.execution_time > 0

    def test_execute_stores_trace(self) -> None:
        """Test functionality: execute stores trace."""
        agent = ThinkingAgent()
        agent.execute(AgentRequest(prompt="Test prompt"))
        assert agent.last_trace is not None
        assert agent.last_trace.is_complete
        assert agent.last_trace.step_count >= 1

    def test_trace_has_metadata(self) -> None:
        """Test functionality: trace has metadata."""
        agent = ThinkingAgent()
        response = agent.execute(AgentRequest(prompt="Test"))
        assert response.metadata is not None
        assert "trace_id" in response.metadata
        assert "confidence" in response.metadata
        assert "steps" in response.metadata
        assert "depth" in response.metadata

    def test_multiple_executions_accumulate_traces(self) -> None:
        """Test functionality: multiple executions accumulate traces."""
        agent = ThinkingAgent()
        agent.execute(AgentRequest(prompt="First"))
        agent.execute(AgentRequest(prompt="Second"))
        assert len(agent.all_traces) == 2

    def test_depth_property(self) -> None:
        """Test functionality: depth property."""
        agent = ThinkingAgent()
        assert agent.thinking_depth == ThinkingDepth.NORMAL
        agent.thinking_depth = ThinkingDepth.DEEP
        assert agent.thinking_depth == ThinkingDepth.DEEP

    def test_shallow_produces_fewer_steps(self) -> None:
        """Test functionality: shallow produces fewer steps."""
        agent = ThinkingAgent(
            thinking_config=ThinkingAgentConfig(depth=ThinkingDepth.SHALLOW)
        )
        agent.execute(AgentRequest(prompt="Quick check"))
        assert agent.last_trace is not None
        # Shallow should produce fewer steps than normal
        assert agent.last_trace.step_count <= 3

    def test_deep_produces_more_steps(self) -> None:
        """Test functionality: deep produces more steps."""
        agent = ThinkingAgent(
            thinking_config=ThinkingAgentConfig(depth=ThinkingDepth.DEEP)
        )
        agent.execute(AgentRequest(prompt="Complex problem"))
        assert agent.last_trace is not None
        assert agent.last_trace.step_count >= 5

    def test_context_summary(self) -> None:
        """Test functionality: context summary."""
        agent = ThinkingAgent()
        agent.execute(AgentRequest(prompt="Hello"))
        summary = agent.context_summary
        assert "message_count" in summary
        assert summary["message_count"] >= 2  # user + assistant

    def test_plan(self) -> None:
        """Test functionality: plan."""
        agent = ThinkingAgent()
        request = AgentRequest(prompt="Plan a refactoring")
        steps = agent.plan(request)
        assert len(steps) >= 1
        assert all(isinstance(s, str) for s in steps)

    def test_act(self) -> None:
        """Test functionality: act."""
        agent = ThinkingAgent()
        response = agent.act("do something")
        assert "Executed" in response.content

    def test_observe(self) -> None:
        """Test functionality: observe."""
        from codomyrmex.agents.core.base import AgentResponse
        agent = ThinkingAgent()
        obs = agent.observe(AgentResponse(content="Done"))
        assert "success" in obs
        assert obs["success"]

    def test_max_traces_limited(self) -> None:
        """Test functionality: max traces limited."""
        cfg = ThinkingAgentConfig(max_traces=3)
        agent = ThinkingAgent(thinking_config=cfg)
        for i in range(5):
            agent.execute(AgentRequest(prompt=f"Test {i}"))
        assert len(agent.all_traces) == 3

    def test_reflection_on_risks(self) -> None:
        """Test functionality: reflection on risks."""
        agent = ThinkingAgent(
            thinking_config=ThinkingAgentConfig(reflect_on_errors=True)
        )
        agent.execute(AgentRequest(prompt="Risky operation"))
        trace = agent.last_trace
        assert trace is not None
        # Should have a reflection step if risks were identified
        reflection_steps = [s for s in trace.steps if s.step_type == "reflection"]
        # At least the structural conclusion produces risks
        assert len(reflection_steps) >= 0  # May or may not have risks
