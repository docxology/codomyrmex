"""Tests for core agent infrastructure: BaseAgent, AgentRequest, AgentResponse, AgentCapabilities, ToolRegistry, ReActAgent."""

import pytest

from codomyrmex.agents.core.base import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.agents.core.config import AgentConfig
from codomyrmex.agents.core.registry import Tool, ToolRegistry
from codomyrmex.agents.core.react import ReActAgent


# ---------------------------------------------------------------------------
# Concrete subclass for testing (zero-mock — real objects only)
# ---------------------------------------------------------------------------
class EchoAgent(BaseAgent):
    """Minimal agent that echoes its prompt back."""

    def __init__(self, name: str = "echo", config: dict | None = None):
        super().__init__(
            name=name,
            capabilities=[AgentCapabilities.TEXT_COMPLETION],
            config=config,
        )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        return AgentResponse(content=f"echo: {request.prompt}")

    def _stream_impl(self, request):
        yield f"echo: {request.prompt}"


# ── AgentRequest ──────────────────────────────────────────────────────────


class TestAgentRequest:
    def test_defaults(self):
        req = AgentRequest(prompt="hello")
        assert req.prompt == "hello"
        assert req.context is None or isinstance(req.context, dict)

    def test_with_context(self):
        req = AgentRequest(prompt="hi", context={"k": "v"})
        assert req.context["k"] == "v"


# ── AgentResponse ─────────────────────────────────────────────────────────


class TestAgentResponse:
    def test_success(self):
        resp = AgentResponse(content="done")
        assert resp.content == "done"
        assert resp.is_success()

    def test_failure(self):
        resp = AgentResponse(content="", error="bad")
        assert not resp.is_success()


# ── AgentCapabilities ─────────────────────────────────────────────────────


class TestAgentCapabilities:
    def test_enum_values_exist(self):
        """Verify key enum members are defined."""
        for name in [
            "CODE_GENERATION",
            "CODE_EDITING",
            "CODE_ANALYSIS",
            "TEXT_COMPLETION",
            "STREAMING",
            "MULTI_TURN",
        ]:
            assert hasattr(AgentCapabilities, name)


# ── BaseAgent ─────────────────────────────────────────────────────────────


class TestBaseAgent:
    def test_lifecycle(self):
        agent = EchoAgent()
        assert agent.name == "echo"
        caps = agent.get_capabilities()
        assert AgentCapabilities.TEXT_COMPLETION in caps

    def test_supports_capability(self):
        agent = EchoAgent()
        assert agent.supports_capability(AgentCapabilities.TEXT_COMPLETION)
        assert not agent.supports_capability(AgentCapabilities.CODE_GENERATION)

    def test_execute(self):
        agent = EchoAgent()
        resp = agent.execute(AgentRequest(prompt="ping"))
        assert resp.is_success()
        assert "ping" in resp.content

    def test_validate_empty_prompt(self):
        agent = EchoAgent()
        # BaseAgent.execute catches exceptions and wraps them in AgentResponse
        resp = agent.execute(AgentRequest(prompt=""))
        assert not resp.is_success()
        assert resp.error is not None

    def test_test_connection(self):
        agent = EchoAgent()
        result = agent.test_connection()
        assert result is True


# ── AgentConfig ───────────────────────────────────────────────────────────


class TestAgentConfig:
    def test_dataclass_fields(self):
        """AgentConfig is a dataclass — verify field access and to_dict."""
        cfg = AgentConfig()
        # Uses default values; attributes are set directly
        assert cfg.jules_command == "jules"
        cfg.jules_command = "my_jules"
        assert cfg.jules_command == "my_jules"

    def test_to_dict(self):
        cfg = AgentConfig()
        d = cfg.to_dict()
        assert isinstance(d, dict)
        assert "jules_command" in d

    def test_validate(self):
        cfg = AgentConfig()
        errors = cfg.validate()
        assert isinstance(errors, list)


# ── ToolRegistry ──────────────────────────────────────────────────────────


class TestToolRegistry:
    def test_register_and_list(self):
        reg = ToolRegistry()
        tool = Tool(
            name="add",
            func=lambda a, b: a + b,
            description="Add two numbers",
            args_schema={"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}},
        )
        reg.register(tool)
        assert len(reg.list_tools()) == 1
        assert reg.get_tool("add") is tool

    def test_execute(self):
        reg = ToolRegistry()
        reg.register(Tool(
            name="double",
            func=lambda x: x * 2,
            description="Double",
            args_schema={},
        ))
        assert reg.execute("double", x=5) == 10

    def test_get_schemas(self):
        reg = ToolRegistry()
        reg.register(Tool(name="t", func=lambda: 1, description="d", args_schema={}))
        schemas = reg.get_schemas()
        assert len(schemas) == 1
        assert schemas[0]["name"] == "t"

    def test_register_function(self):
        reg = ToolRegistry()

        def greet(name: str) -> str:
            """Say hello."""
            return f"Hello, {name}!"

        reg.register_function(greet)
        assert reg.execute("greet", name="World") == "Hello, World!"

    def test_execute_missing_raises(self):
        reg = ToolRegistry()
        with pytest.raises(ValueError, match="not found"):
            reg.execute("nonexistent")


# ── ReActAgent ────────────────────────────────────────────────────────────


class TestReActAgent:
    def test_tool_execution_via_call_prefix(self):
        """Test the 'call:' prefix direct tool invocation."""
        reg = ToolRegistry()
        reg.register(Tool(
            name="square",
            func=lambda x: x ** 2,
            description="Square a number",
            args_schema={},
        ))
        agent = ReActAgent(name="react", tool_registry=reg)
        resp = agent.execute(AgentRequest(prompt='call: square {"x": 4}'))
        assert resp.is_success()
        assert "16" in resp.content

    def test_no_tool_fallback(self):
        reg = ToolRegistry()
        agent = ReActAgent(name="react", tool_registry=reg)
        resp = agent.execute(AgentRequest(prompt="what time is it?"))
        assert resp.is_success()
