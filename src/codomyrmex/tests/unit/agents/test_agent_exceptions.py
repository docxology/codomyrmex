"""Comprehensive tests for agents.core.exceptions — zero-mock.

Covers all exception classes: AgentError, AgentTimeoutError, AgentConfigurationError,
JulesError, ClaudeError (with is_retryable), CodexError, OpenCodeError, GeminiError,
MistralVibeError, and all other provider-specific exceptions.
"""

import pytest

from codomyrmex.agents.core.exceptions import (
    AgentConfigurationError,
    AgentError,
    AgentTimeoutError,
    ClaudeError,
    CodexError,
    GeminiError,
    JulesError,
    MistralVibeError,
    OpenCodeError,
)

# ---------------------------------------------------------------------------
# AgentError (base)
# ---------------------------------------------------------------------------


class TestAgentError:
    def test_is_exception(self):
        e = AgentError("test error")
        assert isinstance(e, Exception)
        assert "test error" in str(e)


# ---------------------------------------------------------------------------
# AgentTimeoutError
# ---------------------------------------------------------------------------


class TestAgentTimeoutError:
    def test_default_message(self):
        e = AgentTimeoutError()
        assert "timed out" in str(e).lower()

    def test_custom_message(self):
        e = AgentTimeoutError("Custom timeout")
        assert "Custom timeout" in str(e)

    def test_with_timeout_value(self):
        e = AgentTimeoutError(timeout=30.0)
        assert e.context.get("timeout") == 30.0

    def test_inherits_agent_error(self):
        e = AgentTimeoutError()
        assert isinstance(e, AgentError)


# ---------------------------------------------------------------------------
# AgentConfigurationError
# ---------------------------------------------------------------------------


class TestAgentConfigurationError:
    def test_default_message(self):
        e = AgentConfigurationError()
        assert "configuration" in str(e).lower()

    def test_with_config_key(self):
        e = AgentConfigurationError(config_key="API_KEY")
        assert e.context.get("config_key") == "API_KEY"

    def test_inherits_agent_error(self):
        e = AgentConfigurationError()
        assert isinstance(e, AgentError)


# ---------------------------------------------------------------------------
# JulesError
# ---------------------------------------------------------------------------


class TestJulesError:
    def test_default_message(self):
        e = JulesError()
        assert "jules" in str(e).lower()

    def test_with_command_and_exit_code(self):
        e = JulesError(command="jules run", exit_code=1)
        assert e.context.get("command") == "jules run"
        assert e.context.get("exit_code") == 1


# ---------------------------------------------------------------------------
# ClaudeError
# ---------------------------------------------------------------------------


class TestClaudeError:
    def test_default_message(self):
        e = ClaudeError()
        assert "claude" in str(e).lower()

    def test_with_all_context(self):
        e = ClaudeError(
            message="API limit",
            model="claude-3-opus",
            api_error="rate_limit_exceeded",
            status_code=429,
            retry_after=60.0,
            request_id="req-123",
        )
        assert e.context.get("model") == "claude-3-opus"
        assert e.context.get("status_code") == 429
        assert e.context.get("retry_after") == 60.0
        assert e.context.get("request_id") == "req-123"

    def test_is_retryable_429(self):
        e = ClaudeError(status_code=429)
        assert e.is_retryable  # property, not method

    def test_is_retryable_500(self):
        e = ClaudeError(status_code=500)
        assert e.is_retryable

    def test_not_retryable_400(self):
        e = ClaudeError(status_code=400)
        assert not e.is_retryable

    def test_not_retryable_no_status(self):
        e = ClaudeError()
        assert not e.is_retryable


# ---------------------------------------------------------------------------
# CodexError
# ---------------------------------------------------------------------------


class TestCodexError:
    def test_default_message(self):
        e = CodexError()
        assert "codex" in str(e).lower()

    def test_with_model(self):
        e = CodexError(model="code-davinci-002")
        assert e.context.get("model") == "code-davinci-002"


# ---------------------------------------------------------------------------
# OpenCodeError
# ---------------------------------------------------------------------------


class TestOpenCodeError:
    def test_default_message(self):
        e = OpenCodeError()
        assert "opencode" in str(e).lower()

    def test_with_command(self):
        e = OpenCodeError(command="opencode edit", exit_code=2)
        assert e.context.get("command") == "opencode edit"
        assert e.context.get("exit_code") == 2


# ---------------------------------------------------------------------------
# GeminiError
# ---------------------------------------------------------------------------


class TestGeminiError:
    def test_default_message(self):
        e = GeminiError()
        assert "gemini" in str(e).lower()

    def test_with_context(self):
        e = GeminiError(command="gemini chat", exit_code=1)
        assert e.context.get("command") == "gemini chat"


# ---------------------------------------------------------------------------
# MistralVibeError
# ---------------------------------------------------------------------------


class TestMistralVibeError:
    def test_default_message(self):
        e = MistralVibeError()
        assert "mistral" in str(e).lower()

    def test_with_context(self):
        e = MistralVibeError(command="vibe run", exit_code=3)
        assert e.context.get("exit_code") == 3


# ---------------------------------------------------------------------------
# Cross-cutting
# ---------------------------------------------------------------------------


class TestExceptionHierarchy:
    def test_all_inherit_from_agent_error(self):
        """All agent exceptions should inherit from AgentError."""
        for exc_cls in [
            AgentTimeoutError,
            AgentConfigurationError,
            JulesError,
            ClaudeError,
            CodexError,
            OpenCodeError,
            GeminiError,
            MistralVibeError,
        ]:
            e = exc_cls()
            assert isinstance(e, AgentError), (
                f"{exc_cls.__name__} should inherit AgentError"
            )

    def test_all_have_context_dict(self):
        """All agent exceptions should have a context attribute."""
        for exc_cls in [
            AgentTimeoutError,
            AgentConfigurationError,
            JulesError,
            ClaudeError,
            CodexError,
            OpenCodeError,
            GeminiError,
            MistralVibeError,
        ]:
            e = exc_cls()
            assert hasattr(e, "context"), f"{exc_cls.__name__} should have context"
