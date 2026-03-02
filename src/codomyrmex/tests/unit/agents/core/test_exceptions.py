"""
Unit tests for agents.core.exceptions — Zero-Mock compliant.

Covers: AgentError, AgentTimeoutError, AgentConfigurationError,
JulesError, ClaudeError (with is_retryable), CodexError, OpenCodeError,
GeminiError, MistralVibeError, EveryCodeError, OpenClawError,
SessionError, ExecutionError, ToolError, ContextError.
"""

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
    SessionError,
    ToolError,
)

# ── AgentError (base) ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestAgentError:
    def test_is_exception(self):
        err = AgentError("base error")
        assert isinstance(err, Exception)

    def test_message_in_str(self):
        err = AgentError("something failed")
        assert "something failed" in str(err)


# ── AgentTimeoutError ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestAgentTimeoutError:
    def test_default_message(self):
        err = AgentTimeoutError()
        assert "timed out" in str(err).lower()

    def test_with_timeout(self):
        err = AgentTimeoutError("op timed out", timeout=30.0)
        assert err.context["timeout"] == 30.0

    def test_without_timeout(self):
        err = AgentTimeoutError("timeout")
        assert "timeout" not in err.context

    def test_is_agent_error(self):
        assert isinstance(AgentTimeoutError(), AgentError)


# ── AgentConfigurationError ───────────────────────────────────────────────


@pytest.mark.unit
class TestAgentConfigurationError:
    def test_with_config_key(self):
        err = AgentConfigurationError("bad config", config_key="api_key")
        assert err.context["config_key"] == "api_key"

    def test_without_config_key(self):
        err = AgentConfigurationError("bad config")
        assert "config_key" not in err.context


# ── JulesError ────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestJulesError:
    def test_with_command_and_exit_code(self):
        err = JulesError("Jules failed", command="jules run", exit_code=1)
        assert err.context["command"] == "jules run"
        assert err.context["exit_code"] == 1

    def test_without_optional_fields(self):
        err = JulesError("Jules failed")
        assert "command" not in err.context
        assert "exit_code" not in err.context


# ── ClaudeError ───────────────────────────────────────────────────────────


@pytest.mark.unit
class TestClaudeError:
    def test_all_fields(self):
        err = ClaudeError(
            "API failed",
            model="claude-3",
            api_error="rate_limit",
            status_code=429,
            retry_after=10.0,
            request_id="req-abc",
        )
        assert err.context["model"] == "claude-3"
        assert err.context["api_error"] == "rate_limit"
        assert err.context["status_code"] == 429
        assert err.context["retry_after"] == 10.0
        assert err.context["request_id"] == "req-abc"

    def test_is_retryable_429(self):
        err = ClaudeError(status_code=429)
        assert err.is_retryable is True

    def test_is_retryable_500(self):
        assert ClaudeError(status_code=500).is_retryable is True

    def test_is_retryable_503(self):
        assert ClaudeError(status_code=503).is_retryable is True

    def test_is_retryable_529(self):
        assert ClaudeError(status_code=529).is_retryable is True

    def test_not_retryable_400(self):
        assert ClaudeError(status_code=400).is_retryable is False

    def test_not_retryable_no_status(self):
        assert ClaudeError("no status").is_retryable is False

    def test_without_optional_fields(self):
        err = ClaudeError("failed")
        assert "model" not in err.context
        assert "api_error" not in err.context


# ── CodexError ────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCodexError:
    def test_with_model(self):
        err = CodexError("Codex failed", model="code-davinci")
        assert err.context["model"] == "code-davinci"

    def test_without_model(self):
        err = CodexError("failed")
        assert "model" not in err.context


# ── CLI-style agent errors (OpenCodeError, GeminiError, etc.) ─────────────


@pytest.mark.unit
class TestCliAgentErrors:
    """Test the pattern of command/exit_code errors shared by multiple classes."""

    @pytest.mark.parametrize("ErrorClass", [
        OpenCodeError, GeminiError, MistralVibeError, EveryCodeError, OpenClawError
    ])
    def test_with_command_and_exit_code(self, ErrorClass):
        err = ErrorClass("failed", command="cmd run", exit_code=2)
        assert err.context["command"] == "cmd run"
        assert err.context["exit_code"] == 2

    @pytest.mark.parametrize("ErrorClass", [
        OpenCodeError, GeminiError, MistralVibeError, EveryCodeError, OpenClawError
    ])
    def test_without_optional_fields(self, ErrorClass):
        err = ErrorClass("failed")
        assert "command" not in err.context
        assert "exit_code" not in err.context

    @pytest.mark.parametrize("ErrorClass", [
        OpenCodeError, GeminiError, MistralVibeError, EveryCodeError, OpenClawError
    ])
    def test_is_agent_error(self, ErrorClass):
        assert isinstance(ErrorClass("msg"), AgentError)


# ── SessionError ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSessionError:
    def test_with_session_id(self):
        err = SessionError("session failed", session_id="sess-123")
        assert err.context["session_id"] == "sess-123"

    def test_without_session_id(self):
        err = SessionError("failed")
        assert "session_id" not in err.context


# ── ExecutionError ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestExecutionError:
    def test_all_fields(self):
        err = ExecutionError("exec failed", task_id="t1", action="run_code", exit_code=1)
        assert err.context["task_id"] == "t1"
        assert err.context["action"] == "run_code"
        assert err.context["exit_code"] == 1

    def test_without_optional_fields(self):
        err = ExecutionError("failed")
        assert "task_id" not in err.context
        assert "action" not in err.context


# ── ToolError ─────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestToolError:
    def test_with_tool_name(self):
        err = ToolError("tool failed", tool_name="run_command")
        assert err.context["tool_name"] == "run_command"

    def test_with_tool_input(self):
        err = ToolError("tool failed", tool_input={"cmd": "ls"})
        assert "tool_input" in err.context

    def test_tool_input_truncated_when_long(self):
        long_input = {"data": "x" * 600}
        err = ToolError("failed", tool_input=long_input)
        assert len(err.context["tool_input"]) <= 503  # 500 + "..."

    def test_without_optional_fields(self):
        err = ToolError("failed")
        assert "tool_name" not in err.context


# ── ContextError ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestContextError:
    def test_all_fields(self):
        err = ContextError(
            "context too large",
            context_size=16000,
            max_context=8000,
            context_type="conversation",
        )
        assert err.context["context_size"] == 16000
        assert err.context["max_context"] == 8000
        assert err.context["context_type"] == "conversation"

    def test_without_optional_fields(self):
        err = ContextError("failed")
        assert "context_size" not in err.context
        assert "context_type" not in err.context
