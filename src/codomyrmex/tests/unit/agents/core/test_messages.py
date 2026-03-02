"""
Unit tests for agents.core.messages — Zero-Mock compliant.

Covers: MessageRole, ToolCall, ToolResult, AgentMessage
(factory methods, to_dict/from_dict, to_llm_dict).
"""

import pytest

from codomyrmex.agents.core.messages import (
    AgentMessage,
    MessageRole,
    ToolCall,
    ToolResult,
)

# ── MessageRole ────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMessageRole:
    def test_values(self):
        assert MessageRole.SYSTEM == "system"
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.TOOL == "tool"


# ── ToolCall ───────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestToolCall:
    def test_defaults(self):
        tc = ToolCall(name="my_tool")
        assert tc.name == "my_tool"
        assert tc.arguments == {}
        assert isinstance(tc.call_id, str)
        assert len(tc.call_id) == 12  # uuid4 hex[:12]

    def test_with_arguments(self):
        tc = ToolCall(name="search", arguments={"query": "hello"})
        assert tc.arguments["query"] == "hello"


# ── ToolResult ─────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestToolResult:
    def test_success_when_no_error(self):
        tr = ToolResult(call_id="abc", output="result")
        assert tr.is_success is True

    def test_not_success_with_error(self):
        tr = ToolResult(call_id="abc", error="failed")
        assert tr.is_success is False

    def test_default_output_is_none(self):
        tr = ToolResult(call_id="abc")
        assert tr.output is None


# ── AgentMessage — factory methods ────────────────────────────────────────


@pytest.mark.unit
class TestAgentMessageFactories:
    def test_system_factory(self):
        msg = AgentMessage.system("you are helpful")
        assert msg.role == MessageRole.SYSTEM
        assert msg.content == "you are helpful"

    def test_user_factory(self):
        msg = AgentMessage.user("hello")
        assert msg.role == MessageRole.USER

    def test_assistant_factory(self):
        msg = AgentMessage.assistant("hi there")
        assert msg.role == MessageRole.ASSISTANT

    def test_tool_factory(self):
        msg = AgentMessage.tool("result text")
        assert msg.role == MessageRole.TOOL
        assert msg.tool_results == []

    def test_tool_factory_with_results(self):
        results = [ToolResult(call_id="c1", output="done")]
        msg = AgentMessage.tool("done", results=results)
        assert len(msg.tool_results) == 1

    def test_auto_message_id(self):
        msg = AgentMessage.user("test")
        assert isinstance(msg.message_id, str)
        assert len(msg.message_id) == 32  # uuid4 hex

    def test_unique_message_ids(self):
        m1 = AgentMessage.user("test")
        m2 = AgentMessage.user("test")
        assert m1.message_id != m2.message_id


# ── AgentMessage — to_dict / from_dict ────────────────────────────────────


@pytest.mark.unit
class TestAgentMessageSerialization:
    def test_to_dict_basic(self):
        msg = AgentMessage.user("hello")
        d = msg.to_dict()
        assert d["role"] == "user"
        assert d["content"] == "hello"
        assert "message_id" in d
        assert "timestamp" in d

    def test_to_dict_excludes_empty_tool_calls(self):
        msg = AgentMessage.user("hello")
        d = msg.to_dict()
        assert "tool_calls" not in d

    def test_to_dict_includes_tool_calls_when_set(self):
        msg = AgentMessage.user("test")
        msg.tool_calls.append(ToolCall(name="search", arguments={"q": "hi"}))
        d = msg.to_dict()
        assert "tool_calls" in d
        assert d["tool_calls"][0]["name"] == "search"

    def test_to_dict_includes_metadata_when_set(self):
        msg = AgentMessage.user("test", metadata={"req_id": "123"})
        d = msg.to_dict()
        assert d["metadata"]["req_id"] == "123"

    def test_from_dict_roundtrip(self):
        original = AgentMessage.assistant("I can help", metadata={"step": 1})
        d = original.to_dict()
        restored = AgentMessage.from_dict(d)
        assert restored.role == MessageRole.ASSISTANT
        assert restored.content == "I can help"
        assert restored.message_id == original.message_id

    def test_from_dict_with_tool_calls(self):
        d = {
            "role": "user",
            "content": "run search",
            "tool_calls": [{"name": "search", "arguments": {"q": "test"}, "call_id": "abc123"}],
            "timestamp": "2025-01-01T00:00:00+00:00",
        }
        msg = AgentMessage.from_dict(d)
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0].name == "search"

    def test_from_dict_with_tool_results(self):
        d = {
            "role": "tool",
            "content": "result",
            "tool_results": [{"call_id": "c1", "output": "done", "error": None}],
            "timestamp": "2025-01-01T00:00:00+00:00",
        }
        msg = AgentMessage.from_dict(d)
        assert len(msg.tool_results) == 1
        assert msg.tool_results[0].output == "done"


# ── AgentMessage — to_llm_dict ────────────────────────────────────────────


@pytest.mark.unit
class TestAgentMessageLLMDict:
    def test_to_llm_dict_minimal(self):
        msg = AgentMessage.user("hello")
        d = msg.to_llm_dict()
        assert d == {"role": "user", "content": "hello"}

    def test_to_llm_dict_excludes_extras(self):
        msg = AgentMessage.system("sys", metadata={"k": "v"})
        d = msg.to_llm_dict()
        assert set(d.keys()) == {"role", "content"}
