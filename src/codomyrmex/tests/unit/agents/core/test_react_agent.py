"""
Unit tests for agents.core.react — Zero-Mock compliant.

Covers: ReActAgent plan/act/observe/_execute_impl, direct tool calls,
LLM-less fallback path, _parse_action_args, stream().
"""


import pytest

from codomyrmex.agents.core.base import AgentCapabilities, AgentRequest, AgentResponse
from codomyrmex.agents.core.react import ReActAgent
from codomyrmex.agents.core.registry import ToolRegistry

# ── Helpers ────────────────────────────────────────────────────────────────


def _make_registry(*funcs) -> ToolRegistry:
    reg = ToolRegistry()
    for fn in funcs:
        reg.register_function(fn)
    return reg


def _echo(text: str) -> str:
    """Echo the input text."""
    return text


def _add(x: int, y: int) -> int:
    """Add two integers."""
    return x + y


def _fail() -> str:
    """Always raises."""
    raise RuntimeError("intentional failure")


# ── Constructor / capabilities ─────────────────────────────────────────────


@pytest.mark.unit
class TestReActAgentInit:
    def test_has_multi_turn_capability(self):
        agent = ReActAgent("a", ToolRegistry())
        assert AgentCapabilities.MULTI_TURN in agent.get_capabilities()

    def test_has_code_execution_capability(self):
        agent = ReActAgent("a", ToolRegistry())
        assert AgentCapabilities.CODE_EXECUTION in agent.get_capabilities()

    def test_default_max_steps(self):
        agent = ReActAgent("a", ToolRegistry())
        assert agent.max_steps == 10

    def test_custom_max_steps(self):
        agent = ReActAgent("a", ToolRegistry(), max_steps=3)
        assert agent.max_steps == 3

    def test_tool_registry_stored(self):
        reg = ToolRegistry()
        agent = ReActAgent("a", reg)
        assert agent.tool_registry is reg


# ── plan() ─────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestReActPlan:
    def test_plan_returns_list(self):
        agent = ReActAgent("a", ToolRegistry())
        request = AgentRequest(prompt="do something")
        plan = agent.plan(request)
        assert isinstance(plan, list)
        assert len(plan) > 0

    def test_plan_with_no_tools(self):
        agent = ReActAgent("a", ToolRegistry())
        plan = agent.plan(AgentRequest(prompt="hello"))
        assert plan[0].startswith("llm_reason_with_tools:")

    def test_plan_includes_tool_names(self):
        reg = _make_registry(_echo, _add)
        agent = ReActAgent("a", reg)
        plan = agent.plan(AgentRequest(prompt="hello"))
        assert "_echo" in plan[0] or "_add" in plan[0]

    def test_plan_call_prefix_extracts_tool(self):
        agent = ReActAgent("a", _make_registry(_echo))
        plan = agent.plan(AgentRequest(prompt="call: _echo foo"))
        assert plan[0] == "call_tool:_echo"

    def test_plan_call_prefix_empty_invalid(self):
        agent = ReActAgent("a", _make_registry())
        plan = agent.plan(AgentRequest(prompt="call:"))
        assert plan[0] == "invalid_call"


# ── act() ──────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestReActAct:
    def test_act_call_tool_success(self):
        reg = _make_registry(_echo)
        agent = ReActAgent("a", reg)
        ctx = {"prompt": 'call: _echo {"text": "hi"}'}
        resp = agent.act("call_tool:_echo", ctx)
        assert resp.is_success()
        assert "hi" in resp.content

    def test_act_call_tool_missing_tool(self):
        agent = ReActAgent("a", ToolRegistry())
        resp = agent.act("call_tool:nonexistent", {"prompt": "call: nonexistent"})
        assert not resp.is_success()
        assert resp.error is not None

    def test_act_call_tool_raises_returns_error(self):
        reg = _make_registry(_fail)
        agent = ReActAgent("a", reg)
        resp = agent.act("call_tool:_fail", {"prompt": "call: _fail"})
        assert not resp.is_success()

    def test_act_llm_reason_no_llm_client(self):
        reg = _make_registry(_echo)
        agent = ReActAgent("a", reg, llm_client=None)
        resp = agent.act("llm_reason_with_tools:_echo", {"prompt": "hello"})
        assert resp.is_success()
        # Falls back to "Processed request" message
        assert "Processed request" in resp.content or resp.is_success()

    def test_act_unknown_action(self):
        agent = ReActAgent("a", ToolRegistry())
        resp = agent.act("totally_unknown_action", {})
        assert not resp.is_success()
        assert resp.error == "unknown_action"


# ── observe() ─────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestReActObserve:
    def test_observe_success_response(self):
        agent = ReActAgent("a", ToolRegistry())
        resp = AgentResponse(content="result", metadata={"key": "val"})
        obs = agent.observe(resp)
        assert obs["success"] is True
        assert obs["content"] == "result"
        assert obs["error"] is None

    def test_observe_error_response(self):
        agent = ReActAgent("a", ToolRegistry())
        resp = AgentResponse(content="", error="some error")
        obs = agent.observe(resp)
        assert obs["success"] is False
        assert obs["error"] == "some error"

    def test_observe_includes_metadata(self):
        agent = ReActAgent("a", ToolRegistry())
        resp = AgentResponse(content="ok", metadata={"steps_taken": 2})
        obs = agent.observe(resp)
        assert obs["metadata"]["steps_taken"] == 2


# ── _execute_impl (full loop) ──────────────────────────────────────────────


@pytest.mark.unit
class TestReActExecuteImpl:
    def test_execute_direct_call_succeeds(self):
        reg = _make_registry(_echo)
        agent = ReActAgent("a", reg)
        req = AgentRequest(prompt='call: _echo {"text": "hi"}')
        resp = agent.execute(req)
        assert resp.is_success()

    def test_execute_llm_fallback_no_client(self):
        reg = _make_registry(_echo)
        agent = ReActAgent("a", reg)
        req = AgentRequest(prompt="tell me something")
        resp = agent.execute(req)
        assert resp.is_success()
        assert resp.content  # Non-empty

    def test_execute_stops_on_action_failure(self):
        # When plan returns a call_tool action that fails, execution stops
        reg = _make_registry(_fail)
        agent = ReActAgent("a", reg)
        req = AgentRequest(prompt='call: _fail {}')
        resp = agent.execute(req)
        # Should get back an error result
        assert not resp.is_success()


# ── _parse_action_args ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestParseActionArgs:
    def test_empty_args(self):
        agent = ReActAgent("a", ToolRegistry())
        result = agent._parse_action_args("tool_name")
        assert result == {}

    def test_json_args(self):
        agent = ReActAgent("a", ToolRegistry())
        result = agent._parse_action_args('tool_name {"key": "value", "n": 42}')
        assert result["key"] == "value"
        assert result["n"] == 42

    def test_key_value_args(self):
        agent = ReActAgent("a", ToolRegistry())
        result = agent._parse_action_args("tool_name key=hello count=3")
        assert result["key"] == "hello"
        assert result["count"] == 3  # JSON-parsed int

    def test_key_value_string_fallback(self):
        agent = ReActAgent("a", ToolRegistry())
        result = agent._parse_action_args("tool_name name=Alice")
        assert result["name"] == "Alice"

    def test_invalid_json_falls_back_to_kv(self):
        agent = ReActAgent("a", ToolRegistry())
        result = agent._parse_action_args("tool_name {bad json}")
        # falls through to key=value parse (no = in {bad json})
        assert isinstance(result, dict)


# ── stream() ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestReActStream:
    def test_stream_yields_content(self):
        reg = _make_registry(_echo)
        agent = ReActAgent("a", reg)
        req = AgentRequest(prompt="call: _echo")
        chunks = list(agent.stream(req))
        assert len(chunks) == 1
        assert isinstance(chunks[0], str)
