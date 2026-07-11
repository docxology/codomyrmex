"""Tests for agents.core.exceptions."""

import pytest

from codomyrmex.agents.core.exceptions import (
    AgentConfigurationError,
    AgentError,
    AgentTimeoutError,
    ClaudeError,
    CodexError,
    ContextError,
    EveryCodeError,
    ExecutionError,
    GeminiError,
    JulesError,
    MistralVibeError,
    OpenClawError,
    OpenCodeError,
    PaperclipError,
    SessionError,
    ToolError,
)
from codomyrmex.exceptions import CodomyrmexError


class TestAgentErrorHierarchy:
    def test_agent_error_is_codomyrmex_error(self):
        e = AgentError("base error")
        assert isinstance(e, CodomyrmexError)

    def test_agent_error_message(self):
        e = AgentError("something went wrong")
        assert "something went wrong" in str(e)

    def test_timeout_is_agent_error(self):
        assert issubclass(AgentTimeoutError, AgentError)

    def test_config_is_agent_error(self):
        assert issubclass(AgentConfigurationError, AgentError)


class TestAgentTimeoutError:
    def test_default_message(self):
        e = AgentTimeoutError()
        assert "timed out" in str(e).lower()

    def test_with_timeout_value(self):
        e = AgentTimeoutError(timeout=30.0)
        assert e.context["timeout"] == 30.0

    def test_without_timeout_value(self):
        e = AgentTimeoutError("Slow!")
        assert "timeout" not in e.context

    def test_custom_message(self):
        e = AgentTimeoutError("Custom timeout message", timeout=10.0)
        assert "Custom timeout message" in str(e)
        assert e.context["timeout"] == 10.0

    def test_is_exception(self):
        with pytest.raises(AgentTimeoutError):
            raise AgentTimeoutError("timeout!")


class TestAgentConfigurationError:
    def test_default_message(self):
        e = AgentConfigurationError()
        assert "configuration" in str(e).lower()

    def test_with_config_key(self):
        e = AgentConfigurationError(config_key="api_key")
        assert e.context["config_key"] == "api_key"

    def test_without_config_key(self):
        e = AgentConfigurationError("bad config")
        assert "config_key" not in e.context


class TestJulesError:
    def test_default_message(self):
        e = JulesError()
        assert (
            "Jules" in str(e) or "jules" in str(e).lower() or "failed" in str(e).lower()
        )

    def test_with_command_and_exit_code(self):
        e = JulesError(command="jules run", exit_code=1)
        assert e.context["command"] == "jules run"
        assert e.context["exit_code"] == 1

    def test_without_command(self):
        e = JulesError("Jules failed")
        assert "command" not in e.context
        assert "exit_code" not in e.context

    def test_exit_code_zero_stored(self):
        e = JulesError(exit_code=0)
        assert e.context["exit_code"] == 0


class TestClaudeError:
    def test_default_message(self):
        e = ClaudeError()
        assert "Claude" in str(e) or "failed" in str(e).lower()

    def test_with_all_fields(self):
        e = ClaudeError(
            model="claude-3",
            api_error="rate limited",
            status_code=429,
            retry_after=60.0,
            request_id="req-abc",
        )
        assert e.context["model"] == "claude-3"
        assert e.context["api_error"] == "rate limited"
        assert e.context["status_code"] == 429
        assert e.context["retry_after"] == 60.0
        assert e.context["request_id"] == "req-abc"

    def test_is_retryable_429(self):
        e = ClaudeError(status_code=429)
        assert e.is_retryable is True

    def test_is_retryable_500(self):
        e = ClaudeError(status_code=500)
        assert e.is_retryable is True

    def test_is_retryable_503(self):
        e = ClaudeError(status_code=503)
        assert e.is_retryable is True

    def test_not_retryable_400(self):
        e = ClaudeError(status_code=400)
        assert e.is_retryable is False

    def test_not_retryable_no_status(self):
        e = ClaudeError()
        assert e.is_retryable is False

    def test_is_retryable_529(self):
        e = ClaudeError(status_code=529)
        assert e.is_retryable is True


class TestCodexError:
    def test_default_message(self):
        e = CodexError()
        assert "Codex" in str(e) or "failed" in str(e).lower()

    def test_with_model(self):
        e = CodexError(model="codex-cushman")
        assert e.context["model"] == "codex-cushman"

    def test_without_model(self):
        e = CodexError("Codex failed")
        assert "model" not in e.context


class TestCLIAgentErrors:
    """Tests for CLI wrapper agent exceptions (OpenCode, Gemini, MistralVibe, etc.)."""

    def test_open_code_error_with_exit_code(self):
        e = OpenCodeError(command="opencode run", exit_code=2)
        assert e.context["command"] == "opencode run"
        assert e.context["exit_code"] == 2

    def test_gemini_error_default(self):
        e = GeminiError()
        assert isinstance(e, AgentError)

    def test_mistral_vibe_error_is_agent_error(self):
        e = MistralVibeError()
        assert isinstance(e, AgentError)

    def test_every_code_error_with_command(self):
        e = EveryCodeError(command="everycode start")
        assert e.context["command"] == "everycode start"

    def test_open_claw_error_without_args(self):
        e = OpenClawError()
        assert isinstance(e, AgentError)
        assert "command" not in e.context


class TestSessionError:
    def test_with_session_id(self):
        e = SessionError(session_id="sess-xyz")
        assert e.context["session_id"] == "sess-xyz"

    def test_without_session_id(self):
        e = SessionError("Session failed")
        assert "session_id" not in e.context


class TestExecutionError:
    def test_with_all_fields(self):
        e = ExecutionError(task_id="task-1", action="run", exit_code=1)
        assert e.context["task_id"] == "task-1"
        assert e.context["action"] == "run"
        assert e.context["exit_code"] == 1

    def test_exit_code_zero_stored(self):
        e = ExecutionError(exit_code=0)
        assert e.context["exit_code"] == 0

    def test_without_optional_fields(self):
        e = ExecutionError()
        assert "task_id" not in e.context
        assert "action" not in e.context


class TestToolError:
    def test_with_tool_name(self):
        e = ToolError(tool_name="web_search")
        assert e.context["tool_name"] == "web_search"

    def test_tool_input_stored(self):
        e = ToolError(tool_name="t", tool_input={"query": "hello"})
        assert "tool_input" in e.context

    def test_tool_input_truncated_at_500(self):
        long_input = {"data": "x" * 1000}
        e = ToolError(tool_input=long_input)
        assert len(e.context["tool_input"]) <= 510  # 500 + "..."

    def test_without_tool_input(self):
        e = ToolError(tool_name="t")
        assert "tool_input" not in e.context


class TestContextError:
    def test_with_all_fields(self):
        e = ContextError(
            context_size=5000, max_context=4096, context_type="conversation"
        )
        assert e.context["context_size"] == 5000
        assert e.context["max_context"] == 4096
        assert e.context["context_type"] == "conversation"

    def test_without_optional_fields(self):
        e = ContextError()
        assert "context_size" not in e.context
        assert "max_context" not in e.context


class TestPaperclipError:
    """Tests for PaperclipError — the Paperclip CLI/API exception."""

    def test_is_agent_error(self):
        assert issubclass(PaperclipError, AgentError)

    def test_default_message(self):
        e = PaperclipError()
        assert "Paperclip" in str(e) or "failed" in str(e).lower()

    def test_with_command_and_exit_code(self):
        e = PaperclipError(command="paperclip run", exit_code=1)
        assert e.context["command"] == "paperclip run"
        assert e.context["exit_code"] == 1

    def test_without_command(self):
        e = PaperclipError("Paperclip failed")
        assert "command" not in e.context
        assert "exit_code" not in e.context

    def test_exit_code_zero_stored(self):
        e = PaperclipError(exit_code=0)
        assert e.context["exit_code"] == 0

    def test_is_raiseable(self):
        with pytest.raises(PaperclipError):
            raise PaperclipError("crash!")

    def test_inherits_context_from_agent_error(self):
        e = PaperclipError(command="test", exit_code=42)
        assert isinstance(e.context, dict)
