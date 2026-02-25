"""Tests for ThinkingAgent MCP tools.

Verifies that the 4 thinking MCP tools are importable,
produce correct responses, and handle edge cases.
"""

from __future__ import annotations

from codomyrmex.agents.core.mcp_tools import (
    get_last_trace,
    get_thinking_depth,
    set_thinking_depth,
    think,
)


class TestThinkMCPTool:
    """Tests for the think() MCP tool."""

    def test_think_returns_success(self) -> None:
        """Test functionality: think returns success."""
        result = think("What is 2 + 2?")
        assert result["status"] == "success"
        assert "content" in result
        assert isinstance(result["confidence"], float)
        assert isinstance(result["steps"], int)
        assert result["steps"] >= 1

    def test_think_with_shallow_depth(self) -> None:
        """Test functionality: think with shallow depth."""
        result = think("Simple question", depth="shallow")
        assert result["status"] == "success"
        assert result["depth"] == "shallow"

    def test_think_with_deep_depth(self) -> None:
        """Test functionality: think with deep depth."""
        result = think("Complex architectural question", depth="deep")
        assert result["status"] == "success"
        assert result["depth"] == "deep"

    def test_think_with_unknown_depth_defaults_normal(self) -> None:
        """Test functionality: think with unknown depth defaults normal."""
        result = think("A question", depth="unknown_xyz")
        assert result["status"] == "success"
        assert result["depth"] == "normal"


class TestGetThinkingDepth:
    """Tests for get_thinking_depth() MCP tool."""

    def test_returns_valid_depth(self) -> None:
        """Test functionality: returns valid depth."""
        result = get_thinking_depth()
        assert result["status"] == "success"
        assert result["depth"] in ("shallow", "normal", "deep")


class TestSetThinkingDepth:
    """Tests for set_thinking_depth() MCP tool."""

    def test_set_shallow(self) -> None:
        """Test functionality: set shallow."""
        result = set_thinking_depth("shallow")
        assert result["status"] == "success"
        assert result["depth"] == "shallow"

    def test_set_deep(self) -> None:
        """Test functionality: set deep."""
        result = set_thinking_depth("deep")
        assert result["status"] == "success"
        assert result["depth"] == "deep"

    def test_set_normal(self) -> None:
        """Test functionality: set normal."""
        result = set_thinking_depth("normal")
        assert result["status"] == "success"
        assert result["depth"] == "normal"

    def test_invalid_depth_returns_error(self) -> None:
        """Test functionality: invalid depth returns error."""
        result = set_thinking_depth("extreme")
        assert result["status"] == "error"
        assert "Unknown depth" in result["message"]


class TestGetLastTrace:
    """Tests for get_last_trace() MCP tool."""

    def test_after_think_returns_trace(self) -> None:
        """Test functionality: after think returns trace."""
        # First ensure there's a trace
        think("Generate a trace for testing")
        result = get_last_trace()
        assert result["status"] == "success"
        assert "trace_id" in result
        assert isinstance(result["steps"], int)
        assert isinstance(result["confidence"], float)
        assert result["is_complete"] is True
        assert result["conclusion"]["action"] is not None

    def test_trace_has_expected_structure(self) -> None:
        """Test functionality: trace has expected structure."""
        think("Another test prompt")
        result = get_last_trace()
        assert result["status"] == "success"
        assert "depth" in result
        assert result["depth"] in ("shallow", "normal", "deep")


class TestThinkingAgentKnowledgeWiring:
    """Test that ThinkingAgent accepts and uses a knowledge retriever."""

    def test_agent_without_retriever(self) -> None:
        """Test functionality: agent without retriever."""
        from codomyrmex.agents.core.base import AgentRequest
        from codomyrmex.agents.core.thinking_agent import ThinkingAgent

        agent = ThinkingAgent()
        assert agent.knowledge_retriever is None

        # Should still work fine without retriever
        response = agent.execute(AgentRequest(prompt="Test without knowledge"))
        assert response.content

    def test_agent_with_retriever_property(self) -> None:
        """Test functionality: agent with retriever property."""
        from codomyrmex.agents.core.thinking_agent import ThinkingAgent

        agent = ThinkingAgent()
        assert agent.knowledge_retriever is None

        # Set a mock-free retriever object via property
        class FakeRetriever:
            def retrieve(self, query: str):
                from types import SimpleNamespace
                return SimpleNamespace(
                    entities=[],
                    relationships=[],
                    confidence=0.5,
                )

        retriever = FakeRetriever()
        agent.knowledge_retriever = retriever
        assert agent.knowledge_retriever is retriever

    def test_agent_executes_with_retriever(self) -> None:
        """Test functionality: agent executes with retriever."""
        from types import SimpleNamespace

        from codomyrmex.agents.core.base import AgentRequest
        from codomyrmex.agents.core.thinking_agent import ThinkingAgent

        class FakeRetriever:
            called_with: str | None = None

            def retrieve(self, query: str):
                self.called_with = query
                return SimpleNamespace(
                    entities=[],
                    relationships=[],
                    confidence=0.75,
                )

        retriever = FakeRetriever()
        agent = ThinkingAgent(knowledge_retriever=retriever)
        response = agent.execute(AgentRequest(prompt="Knowledge test"))

        assert response.content
        assert retriever.called_with == "Knowledge test"

    def test_agent_survives_retriever_failure(self) -> None:
        """Test functionality: agent survives retriever failure."""
        from codomyrmex.agents.core.base import AgentRequest
        from codomyrmex.agents.core.thinking_agent import ThinkingAgent

        class FailingRetriever:
            def retrieve(self, query: str):
                raise RuntimeError("Knowledge graph unavailable")

        agent = ThinkingAgent(knowledge_retriever=FailingRetriever())
        # Should NOT raise — fail-safe behavior
        response = agent.execute(AgentRequest(prompt="Handle failure gracefully"))
        assert response.content
