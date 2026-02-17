"""Tests for agent protocol: AgentMessage, plan/act/observe lifecycle, ToolRegistry.from_mcp.

All tests use real objects — zero mocks.
"""

import json
import uuid

import pytest

from codomyrmex.agents.core.base import (
    AgentCapabilities,
    AgentProtocol,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.agents.core.messages import (
    AgentMessage,
    MessageRole,
    ToolCall,
    ToolResult,
)
from codomyrmex.agents.core.registry import Tool, ToolRegistry
from codomyrmex.agents.core.react import ReActAgent


# ── AgentMessage tests ───────────────────────────────────────────────


class TestAgentMessage:
    """AgentMessage creation, serialization, and factory methods."""

    def test_system_factory(self):
        msg = AgentMessage.system("You are helpful.")
        assert msg.role is MessageRole.SYSTEM
        assert msg.content == "You are helpful."
        assert msg.message_id  # auto-generated

    def test_user_factory(self):
        msg = AgentMessage.user("Hello!")
        assert msg.role is MessageRole.USER
        assert msg.content == "Hello!"

    def test_assistant_factory(self):
        msg = AgentMessage.assistant("Sure.")
        assert msg.role is MessageRole.ASSISTANT

    def test_tool_factory_with_results(self):
        result = ToolResult(call_id="abc", output=42)
        msg = AgentMessage.tool("result", results=[result])
        assert msg.role is MessageRole.TOOL
        assert len(msg.tool_results) == 1
        assert msg.tool_results[0].output == 42

    def test_to_dict_round_trip(self):
        tc = ToolCall(name="greet", arguments={"name": "Ada"})
        original = AgentMessage(
            role=MessageRole.ASSISTANT,
            content="Hi",
            tool_calls=[tc],
        )
        data = original.to_dict()
        restored = AgentMessage.from_dict(data)
        assert restored.role is MessageRole.ASSISTANT
        assert restored.content == "Hi"
        assert len(restored.tool_calls) == 1
        assert restored.tool_calls[0].name == "greet"

    def test_to_llm_dict(self):
        msg = AgentMessage.user("Test")
        d = msg.to_llm_dict()
        assert d == {"role": "user", "content": "Test"}

    def test_tool_result_is_success(self):
        ok = ToolResult(call_id="1", output="ok")
        fail = ToolResult(call_id="2", error="boom")
        assert ok.is_success is True
        assert fail.is_success is False


# ── BaseAgent protocol default implementations ───────────────────────


class TestAgentProtocolDefaults:
    """BaseAgent surfaces plan, act, observe as methods."""

    def test_base_agent_has_protocol_methods(self):
        assert hasattr(BaseAgent, "plan")
        assert hasattr(BaseAgent, "act")
        assert hasattr(BaseAgent, "observe")


# ── ReActAgent plan→act→observe lifecycle ─────────────────────────────


def _double(x: int = 0) -> int:
    """Double a value."""
    return x * 2


class TestReActLifecycle:
    """End-to-end ReAct lifecycle exercising plan, act, observe."""

    @pytest.fixture()
    def registry(self):
        reg = ToolRegistry()
        reg.register_function(_double, name="double", description="Double a value")
        return reg

    @pytest.fixture()
    def agent(self, registry):
        return ReActAgent(name="test", tool_registry=registry)

    def test_plan_direct_call(self, agent):
        request = AgentRequest(prompt="call: double")
        actions = agent.plan(request)
        assert len(actions) == 1
        assert actions[0].startswith("call_tool:")

    def test_plan_llm_fallback(self, agent):
        request = AgentRequest(prompt="What is 2+2?")
        actions = agent.plan(request)
        assert actions[0].startswith("llm_reason_with_tools:")

    def test_act_direct_tool(self, agent):
        response = agent.act("call_tool:double", {"prompt": 'call: double {"x": 3}'})
        assert response.is_success()
        assert "6" in response.content

    def test_act_unknown_action(self, agent):
        response = agent.act("unknown:foo")
        assert not response.is_success()

    def test_observe_extracts_structure(self, agent):
        response = AgentResponse(content="result", metadata={"k": "v"})
        obs = agent.observe(response)
        assert obs["success"] is True
        assert obs["content"] == "result"
        assert obs["metadata"] == {"k": "v"}

    def test_execute_direct_call(self, agent):
        request = AgentRequest(prompt='call: double {"x": 5}')
        response = agent.execute(request)
        assert response.is_success()
        assert "10" in response.content

    def test_execute_no_llm(self, agent):
        """Without an LLM client, the agent gracefully returns available tools."""
        request = AgentRequest(prompt="What is 2+2?")
        response = agent.execute(request)
        assert response.is_success()
        assert "double" in response.content


# ── ToolRegistry.from_mcp bridge ──────────────────────────────────────


class _FakeMCPTool:
    """Minimal MCP tool stand-in (real object, not a mock)."""

    def __init__(self, name, description, handler, input_schema=None):
        self.name = name
        self.description = description
        self.handler = handler
        self.input_schema = input_schema or {"type": "object", "properties": {}}


class _FakeMCPRegistry:
    """Minimal MCP registry stand-in (real object, not a mock)."""

    def __init__(self, tools):
        self._tools = tools

    def list_tools(self):
        return self._tools


class TestToolRegistryFromMCP:

    def test_bridge_populates_tools(self):
        mcp_tools = [
            _FakeMCPTool("greet", "Say hello", lambda: "hello"),
            _FakeMCPTool("add", "Add two numbers", lambda a, b: a + b),
        ]
        mcp_reg = _FakeMCPRegistry(mcp_tools)
        registry = ToolRegistry.from_mcp(mcp_reg)
        assert len(registry.list_tools()) == 2
        assert registry.get_tool("greet") is not None

    def test_bridge_with_prefix(self):
        mcp_tools = [_FakeMCPTool("ping", "Ping", lambda: "pong")]
        registry = ToolRegistry.from_mcp(_FakeMCPRegistry(mcp_tools), prefix="mcp.")
        assert registry.get_tool("mcp.ping") is not None

    def test_bridge_skips_handler_none(self):
        mcp_tools = [_FakeMCPTool("broken", "No handler", None)]
        registry = ToolRegistry.from_mcp(_FakeMCPRegistry(mcp_tools))
        assert len(registry.list_tools()) == 0

    def test_bridge_invalid_registry_raises(self):
        with pytest.raises(TypeError, match="list_tools"):
            ToolRegistry.from_mcp(object())

    def test_bridged_tool_executes(self):
        mcp_tools = [_FakeMCPTool("inc", "Increment", lambda n: n + 1)]
        registry = ToolRegistry.from_mcp(_FakeMCPRegistry(mcp_tools))
        assert registry.execute("inc", n=5) == 6
