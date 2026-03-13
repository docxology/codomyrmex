"""Tests for agents.core.exceptions."""

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


class TestAgentError:
    def test_basic_instantiation(self):
        e = AgentError("test error")
        assert "test error" in str(e)

    def test_is_codomyrmex_error(self):
        from codomyrmex.exceptions import CodomyrmexError

        assert issubclass(AgentError, CodomyrmexError)


class TestAgentTimeoutError:
    def test_default_message(self):
        e = AgentTimeoutError()
        assert "timed out" in str(e).lower()

    def test_with_timeout(self):
        e = AgentTimeoutError(timeout=30.0)
        assert e.context["timeout"] == 30.0

    def test_without_timeout(self):
        e = AgentTimeoutError()
        assert "timeout" not in e.context

    def test_custom_message(self):
        e = AgentTimeoutError("custom timeout")
        assert "custom timeout" in str(e)


class TestAgentConfigurationError:
    def test_default_message(self):
        e = AgentConfigurationError()
        assert "configuration" in str(e).lower()

    def test_with_config_key(self):
        e = AgentConfigurationError(config_key="api_key")
        assert e.context["config_key"] == "api_key"

    def test_without_config_key(self):
        e = AgentConfigurationError()
        assert "config_key" not in e.context


class TestJulesError:
    def test_default_message(self):
        e = JulesError()
        assert "jules" in str(e).lower() or "failed" in str(e).lower()

    def test_with_command_and_exit_code(self):
        e = JulesError(command="run task", exit_code=1)
        assert e.context["command"] == "run task"
        assert e.context["exit_code"] == 1

    def test_optional_fields(self):
        e = JulesError()
        assert "command" not in e.context
        assert "exit_code" not in e.context


class TestClaudeError:
    def test_default_message(self):
        e = ClaudeError()
        assert "claude" in str(e).lower() or "failed" in str(e).lower()

    def test_full_context(self):
        e = ClaudeError(
            model="claude-3-5-sonnet",
            api_error="rate_limit",
            status_code=429,
            retry_after=60.0,
            request_id="req_abc123",
        )
        assert e.context["model"] == "claude-3-5-sonnet"
        assert e.context["api_error"] == "rate_limit"
        assert e.context["status_code"] == 429
        assert e.context["retry_after"] == 60.0
        assert e.context["request_id"] == "req_abc123"

    def test_is_retryable_rate_limit(self):
        e = ClaudeError(status_code=429)
        assert e.is_retryable is True

    def test_is_retryable_server_errors(self):
        for code in [500, 502, 503, 529]:
            e = ClaudeError(status_code=code)
            assert e.is_retryable is True, f"status {code} should be retryable"

    def test_is_not_retryable_client_error(self):
        e = ClaudeError(status_code=400)
        assert e.is_retryable is False

    def test_is_not_retryable_no_status(self):
        e = ClaudeError()
        assert e.is_retryable is False


class TestExecutionError:
    def test_with_all_fields(self):
        e = ExecutionError(task_id="t1", action="run", exit_code=1)
        assert e.context["task_id"] == "t1"
        assert e.context["action"] == "run"
        assert e.context["exit_code"] == 1

    def test_defaults(self):
        e = ExecutionError()
        assert "task_id" not in e.context


class TestToolError:
    def test_tool_name_stored(self):
        e = ToolError(tool_name="bash")
        assert e.context["tool_name"] == "bash"

    def test_tool_input_truncated_when_long(self):
        long_input = {"key": "x" * 1000}
        e = ToolError(tool_name="bash", tool_input=long_input)
        assert len(e.context["tool_input"]) <= 503  # 500 + "..."

    def test_tool_input_not_truncated_when_short(self):
        short_input = {"key": "val"}
        e = ToolError(tool_name="bash", tool_input=short_input)
        assert "..." not in e.context["tool_input"]


class TestContextError:
    def test_full_context(self):
        e = ContextError(
            context_size=100000, max_context=200000, context_type="conversation"
        )
        assert e.context["context_size"] == 100000
        assert e.context["max_context"] == 200000
        assert e.context["context_type"] == "conversation"


class TestSimpleAgentErrors:
    """Test simple agent error classes with minimal constructors."""

    def test_codex_error(self):
        e = CodexError(model="gpt-4")
        assert e.context["model"] == "gpt-4"

    def test_open_code_error(self):
        e = OpenCodeError(command="run", exit_code=2)
        assert e.context["command"] == "run"
        assert e.context["exit_code"] == 2

    def test_gemini_error(self):
        e = GeminiError(command="gemini run")
        assert e.context["command"] == "gemini run"

    def test_mistral_vibe_error(self):
        e = MistralVibeError(exit_code=1)
        assert e.context["exit_code"] == 1

    def test_every_code_error(self):
        e = EveryCodeError()
        assert isinstance(e, AgentError)

    def test_open_claw_error(self):
        e = OpenClawError(command="claw run", exit_code=0)
        assert e.context["command"] == "claw run"

    def test_session_error(self):
        e = SessionError(session_id="sess_abc")
        assert e.context["session_id"] == "sess_abc"

    def test_all_inherit_from_agent_error(self):
        for cls in [
            CodexError,
            OpenCodeError,
            GeminiError,
            MistralVibeError,
            EveryCodeError,
            OpenClawError,
            SessionError,
        ]:
            assert issubclass(cls, AgentError), (
                f"{cls.__name__} should inherit AgentError"
            )

    def test_gemini_error_with_exit_code(self):
        e = GeminiError(command="gemini run", exit_code=127)
        assert e.context["exit_code"] == 127

    def test_mistral_vibe_error_with_command_and_exit_code(self):
        e = MistralVibeError(command="vibe run", exit_code=2)
        assert e.context["command"] == "vibe run"
        assert e.context["exit_code"] == 2

    def test_every_code_error_with_command(self):
        e = EveryCodeError(command="everycode run")
        assert e.context["command"] == "everycode run"

    def test_every_code_error_with_exit_code(self):
        e = EveryCodeError(command="everycode run", exit_code=1)
        assert e.context["exit_code"] == 1
