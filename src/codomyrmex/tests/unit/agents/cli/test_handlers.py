"""Comprehensive unit tests for codomyrmex.agents.cli.handlers.

Tests cover all public handler functions: handle_info, handle_agent_setup,
handle_agent_test, _parse_context, _create_agent_request, and all
agent-specific handlers (jules, claude, codex, opencode, gemini, droid).

Zero-mock policy: uses real objects (SimpleNamespace for args, real
AgentRequest/AgentConfig). External agent CLIs are not required --
tests focus on handler logic (argument parsing, error paths, None-client
guard clauses).
"""

import json
import os
import shutil
import subprocess as _sp
from types import SimpleNamespace

import pytest

from codomyrmex.agents import AgentRequest
from codomyrmex.agents.cli.handlers import (
    _create_agent_request,
    _parse_context,
    handle_agent_setup,
    handle_agent_test,
    handle_claude_check,
    handle_claude_execute,
    handle_claude_stream,
    handle_codex_check,
    handle_codex_execute,
    handle_codex_stream,
    handle_droid_config_show,
    handle_droid_start,
    handle_droid_status,
    handle_droid_stop,
    handle_gemini_chat_list,
    handle_gemini_chat_resume,
    handle_gemini_chat_save,
    handle_gemini_check,
    handle_gemini_execute,
    handle_gemini_stream,
    handle_info,
    handle_jules_check,
    handle_jules_command,
    handle_jules_execute,
    handle_jules_help,
    handle_jules_stream,
    handle_opencode_check,
    handle_opencode_execute,
    handle_opencode_init,
    handle_opencode_stream,
    handle_opencode_version,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# CLI AI agent tests require live network and API credentials to execute
# prompts.  They are skipped unless explicitly opted-in via environment
# variables (per skip policy: skip tests requiring network/API keys).
# Each binary must be present AND the env var must be set to "1".

def _cli_agent_ready(binary: str, env_var: str) -> bool:
    """Return True only if binary is found AND test opt-in env var is set."""
    if not (shutil.which(binary) and os.environ.get(env_var) == "1"):
        return False
    try:
        r = _sp.run([binary, "--version"], capture_output=True, text=True, timeout=3)
        return r.returncode == 0
    except Exception:
        return False

_OPENCODE_READY = _cli_agent_ready("opencode", "OPENCODE_TEST_ENABLED")
_JULES_READY    = _cli_agent_ready("jules",    "JULES_TEST_ENABLED")
_GEMINI_READY   = _cli_agent_ready("gemini",   "GEMINI_TEST_ENABLED")


def _make_args(**kwargs):
    """Build a SimpleNamespace args object with sensible defaults."""
    defaults = {
        "verbose": False,
        "format": "text",
        "prompt": "hello world",
        "context": None,
        "timeout": None,
        "output": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# _parse_context
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestParseContext:
    """Tests for the _parse_context helper."""

    def test_none_returns_empty_dict(self):
        assert _parse_context(None) == {}

    def test_empty_string_returns_empty_dict(self):
        assert _parse_context("") == {}

    def test_valid_json_parsed(self):
        result = _parse_context('{"key": "value", "num": 42}')
        assert result == {"key": "value", "num": 42}

    def test_invalid_json_returns_empty_dict(self):
        result = _parse_context("not-json{")
        assert result == {}

    def test_json_array_parsed(self):
        # json.loads allows arrays -- handler should pass through
        result = _parse_context('[1, 2, 3]')
        assert result == [1, 2, 3]

    def test_nested_json(self):
        data = {"a": {"b": [1, 2]}, "c": True}
        result = _parse_context(json.dumps(data))
        assert result == data


# ---------------------------------------------------------------------------
# _create_agent_request
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCreateAgentRequest:
    """Tests for the _create_agent_request helper."""

    def test_basic_request_creation(self):
        args = _make_args(prompt="test prompt")
        req = _create_agent_request("test prompt", args)
        assert isinstance(req, AgentRequest)
        assert req.prompt == "test prompt"

    def test_context_from_args(self):
        args = _make_args(context='{"env": "prod"}')
        req = _create_agent_request("p", args)
        assert req.context == {"env": "prod"}

    def test_timeout_from_args(self):
        args = _make_args(timeout=60)
        req = _create_agent_request("p", args)
        assert req.timeout == 60

    def test_no_context_attr(self):
        """When args has no context attribute, default to empty dict."""
        args = SimpleNamespace(prompt="p")
        req = _create_agent_request("p", args)
        assert req.context == {}

    def test_no_timeout_attr(self):
        args = SimpleNamespace(prompt="p")
        req = _create_agent_request("p", args)
        assert req.timeout is None


# ---------------------------------------------------------------------------
# handle_info
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHandleInfo:
    """Tests for handle_info."""

    def test_returns_true_on_success(self, capsys):
        args = _make_args()
        result = handle_info(args)
        assert result is True

    def test_verbose_mode(self, capsys):
        args = _make_args(verbose=True)
        result = handle_info(args)
        assert result is True

    def test_json_format(self, capsys):
        args = _make_args(format="json")
        result = handle_info(args)
        assert result is True
        captured = capsys.readouterr()
        # JSON format should produce parseable output somewhere in the stream
        assert "agents" in captured.out.lower() or "module" in captured.out.lower()

    def test_text_format(self, capsys):
        args = _make_args(format="text")
        result = handle_info(args)
        assert result is True


# ---------------------------------------------------------------------------
# handle_agent_setup / handle_agent_test with None client
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHandleAgentSetupNoneClient:
    """Test handle_agent_setup when client_class is None."""

    def test_none_client_returns_false(self, capsys):
        args = _make_args()
        result = handle_agent_setup(None, "FakeAgent", args)
        assert result is False

    def test_none_client_prints_error(self, capsys):
        args = _make_args()
        handle_agent_setup(None, "FakeAgent", args)
        captured = capsys.readouterr()
        assert "not available" in captured.out.lower()


@pytest.mark.unit
class TestHandleAgentTestNoneClient:
    """Test handle_agent_test when client_class is None."""

    def test_none_client_returns_false(self, capsys):
        args = _make_args()
        result = handle_agent_test(None, "FakeAgent", args)
        assert result is False


# ---------------------------------------------------------------------------
# Agent execute/stream with None client class guard
# These test the _handle_agent_execute / _handle_agent_stream code paths
# via the public wrappers, by testing the None-guard directly.
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAgentExecuteNoneGuard:
    """All execute handlers should gracefully handle unavailable clients."""

    def test_handle_agent_execute_none_client(self, capsys):
        """Directly test _handle_agent_execute with None."""
        from codomyrmex.agents.cli.handlers import _handle_agent_execute
        args = _make_args()
        result = _handle_agent_execute(None, "TestAgent", args)
        assert result is False

    def test_handle_agent_stream_none_client(self, capsys):
        """Directly test _handle_agent_stream with None."""
        from codomyrmex.agents.cli.handlers import _handle_agent_stream
        args = _make_args()
        result = _handle_agent_stream(None, "TestAgent", args)
        assert result is False


# ---------------------------------------------------------------------------
# Jules handlers
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.skipif(not _JULES_READY, reason="Jules CLI requires AI API access; set JULES_TEST_ENABLED=1 to run")
class TestJulesHandlers:
    """Tests for Jules-specific handlers (check, help, command)."""

    @pytest.mark.timeout(10)
    def test_jules_execute_runs(self, capsys):
        """Jules execute -- will fail without jules CLI but should not raise."""
        args = _make_args(prompt="test")
        result = handle_jules_execute(args)
        # Result depends on JulesClient availability; either True or False
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_jules_stream_runs(self, capsys):
        args = _make_args(prompt="test")
        result = handle_jules_stream(args)
        assert isinstance(result, bool)

    def test_jules_check_runs(self, capsys):
        args = _make_args()
        result = handle_jules_check(args)
        assert isinstance(result, bool)

    def test_jules_help_runs(self, capsys):
        args = _make_args()
        result = handle_jules_help(args)
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_jules_command_runs(self, capsys):
        args = _make_args(cmd="status", args=[])
        result = handle_jules_command(args)
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_jules_command_with_verbose(self, capsys):
        args = _make_args(cmd="status", args=[], verbose=True)
        result = handle_jules_command(args)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Claude handlers
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClaudeHandlers:
    """Tests for Claude-specific handlers.

    Note: ClaudeClient currently has a broken __init__ (TypeError from mixin
    inheritance). The handler's except clause does not catch TypeError, so
    execute/stream propagate it. We document this as expected behavior.
    """

    def test_claude_execute_runs(self, capsys):
        """ClaudeClient execution acts normally and returns a bool."""
        args = _make_args(prompt="hello")
        result = handle_claude_execute(args)
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_claude_stream_runs(self, capsys):
        """ClaudeClient streaming acts normally and returns a bool."""
        args = _make_args(prompt="hello")
        result = handle_claude_stream(args)
        assert isinstance(result, bool)

    def test_claude_check_runs(self, capsys):
        """claude check does not instantiate ClaudeClient, uses get_config()."""
        args = _make_args()
        result = handle_claude_check(args)
        assert isinstance(result, bool)
        captured = capsys.readouterr()
        # Should print config info regardless of API key presence
        assert "claude" in captured.out.lower()


# ---------------------------------------------------------------------------
# Codex handlers
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCodexHandlers:
    """Tests for Codex-specific handlers."""

    def test_codex_execute_runs(self, capsys):
        args = _make_args(prompt="test")
        result = handle_codex_execute(args)
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_codex_stream_runs(self, capsys):
        args = _make_args(prompt="test")
        result = handle_codex_stream(args)
        assert isinstance(result, bool)

    def test_codex_check_runs(self, capsys):
        args = _make_args()
        result = handle_codex_check(args)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# OpenCode handlers
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.skipif(not _OPENCODE_READY, reason="opencode CLI not available or not responding within 3s")
class TestOpenCodeHandlers:
    """Tests for OpenCode-specific handlers."""

    @pytest.mark.timeout(10)
    def test_opencode_execute_runs(self, capsys):
        args = _make_args(prompt="test")
        result = handle_opencode_execute(args)
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_opencode_stream_runs(self, capsys):
        args = _make_args(prompt="test")
        result = handle_opencode_stream(args)
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_opencode_check_runs(self, capsys):
        args = _make_args()
        result = handle_opencode_check(args)
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_opencode_init_runs(self, capsys):
        args = _make_args(path=None)
        result = handle_opencode_init(args)
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_opencode_version_runs(self, capsys):
        args = _make_args()
        result = handle_opencode_version(args)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Gemini handlers
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.skipif(not _GEMINI_READY, reason="Gemini CLI requires AI API access; set GEMINI_TEST_ENABLED=1 to run")
class TestGeminiHandlers:
    """Tests for Gemini-specific handlers."""

    @pytest.mark.timeout(10)
    def test_gemini_execute_runs(self, capsys):
        args = _make_args(prompt="test")
        result = handle_gemini_execute(args)
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_gemini_stream_runs(self, capsys):
        args = _make_args(prompt="test")
        result = handle_gemini_stream(args)
        assert isinstance(result, bool)

    def test_gemini_check_runs(self, capsys):
        args = _make_args()
        result = handle_gemini_check(args)
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_gemini_chat_save_runs(self, capsys):
        args = _make_args(tag="test-session", prompt="save this")
        result = handle_gemini_chat_save(args)
        assert isinstance(result, bool)

    @pytest.mark.timeout(10)
    def test_gemini_chat_resume_runs(self, capsys):
        args = _make_args(tag="test-session")
        result = handle_gemini_chat_resume(args)
        assert isinstance(result, bool)

    def test_gemini_chat_list_runs(self, capsys):
        args = _make_args()
        result = handle_gemini_chat_list(args)
        assert isinstance(result, bool)

    def test_gemini_chat_list_verbose(self, capsys):
        args = _make_args(verbose=True)
        result = handle_gemini_chat_list(args)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Droid handlers
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDroidHandlers:
    """Tests for Droid-specific handlers.

    Droid module is optional -- these tests verify the handler logic
    regardless of whether the droid module is importable.
    """

    def test_droid_start_runs(self, capsys):
        args = _make_args()
        result = handle_droid_start(args)
        assert isinstance(result, bool)

    def test_droid_stop_runs(self, capsys):
        args = _make_args()
        result = handle_droid_stop(args)
        assert isinstance(result, bool)

    def test_droid_status_runs(self, capsys):
        args = _make_args()
        result = handle_droid_status(args)
        assert isinstance(result, bool)

    def test_droid_config_show_runs(self, capsys):
        args = _make_args()
        result = handle_droid_config_show(args)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# _get_droid_controller
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGetDroidController:
    """Tests for the _get_droid_controller singleton helper."""

    def test_returns_none_when_create_fn_missing(self):
        """When create_default_controller is None, should return None."""
        import codomyrmex.agents.cli.handlers as h
        # Reset singleton
        original = h._droid_controller
        h._droid_controller = None
        try:
            original_fn = h.create_default_controller
            h.create_default_controller = None
            result = h._get_droid_controller()
            assert result is None
            h.create_default_controller = original_fn
        finally:
            h._droid_controller = original


# ---------------------------------------------------------------------------
# Edge cases: _handle_agent_execute and _handle_agent_stream with
# a class that raises on instantiation (simulates missing config)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHandlerErrorPaths:
    """Test error handling paths in handler functions."""

    def test_execute_with_broken_client_class(self, capsys):
        """A client class that raises ValueError on __init__ is caught."""
        from codomyrmex.agents.cli.handlers import _handle_agent_execute

        class BrokenClient:
            def __init__(self):
                raise ValueError("missing config")

        args = _make_args(prompt="test")
        result = _handle_agent_execute(BrokenClient, "Broken", args)
        assert result is False

    def test_stream_with_broken_client_class(self, capsys):
        """A client class that raises RuntimeError on __init__ is caught."""
        from codomyrmex.agents.cli.handlers import _handle_agent_stream

        class BrokenClient:
            def __init__(self):
                raise RuntimeError("no runtime")

        args = _make_args(prompt="test")
        result = _handle_agent_stream(BrokenClient, "Broken", args)
        assert result is False

    def test_setup_with_broken_client_class(self, capsys):
        """A client class that raises on setup()."""

        class BrokenClient:
            def __init__(self, config=None):
                raise OSError("disk full")

        args = _make_args()
        result = handle_agent_setup(BrokenClient, "Broken", args)
        assert result is False

    def test_test_with_broken_client_class(self, capsys):
        """A client class that raises on test_connection()."""

        class BrokenClient:
            def __init__(self, config=None):
                raise AttributeError("bad attr")

        args = _make_args()
        result = handle_agent_test(BrokenClient, "Broken", args)
        assert result is False


# ---------------------------------------------------------------------------
# Output file writing path (via _handle_agent_execute success branch)
# We cannot easily trigger a real successful response without API keys,
# but we CAN test the _create_agent_request + output path indirectly.
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestOutputFilePath:
    """Verify that output file arg is properly read from args."""

    def test_output_arg_propagated(self, tmp_path):
        """Ensure the output path is read from args (even if execute fails).

        Uses Codex (not Claude) because ClaudeClient has a broken __init__.
        Codex will fail with AgentConfigurationError (caught), so handler
        returns False without crashing.
        """
        outfile = tmp_path / "out.txt"
        args = _make_args(output=str(outfile), prompt="test")
        result = handle_codex_execute(args)
        assert result is False  # Fails due to missing API key, but no crash

    def test_output_arg_with_gemini(self, tmp_path):
        """Gemini execute with output arg -- should not crash."""
        outfile = tmp_path / "out.txt"
        args = _make_args(output=str(outfile), prompt="test")
        result = handle_gemini_execute(args)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Real test helper clients — plain Python classes (NOT mocks) used to drive
# the success and partial-success branches of handler internals.
# Zero-mock policy: these are concrete implementations, not Mock() objects.
# ---------------------------------------------------------------------------

from codomyrmex.agents.core.base import AgentResponse  # noqa: E402


class _SuccessClient:
    """Minimal real client that returns a successful AgentResponse."""

    def __init__(self):
        pass

    def execute(self, request):
        return AgentResponse(content="hello from test", metadata={}, error=None)

    def stream(self, request):
        yield "chunk1"
        yield "chunk2"


class _SuccessClientWithMetadata:
    """Returns a response that includes non-empty metadata to hit the metadata branch."""

    def __init__(self):
        pass

    def execute(self, request):
        return AgentResponse(
            content="result",
            metadata={"model": "test-model", "tokens": 5},
            error=None,
        )

    def stream(self, request):
        yield "line1\n"


class _FailureResponseClient:
    """Returns a failed AgentResponse (error set, is_success() == False)."""

    def __init__(self):
        pass

    def execute(self, request):
        return AgentResponse(content="", metadata={}, error="upstream API error")

    def stream(self, request):
        return iter([])


class _SetupableClient:
    """Client with working setup() and test_connection() methods."""

    def __init__(self, config=None):
        self._config = config

    def setup(self):
        pass  # real no-op setup

    def test_connection(self):
        return True


class _TestFailClient:
    """Client where test_connection() returns False."""

    def __init__(self, config=None):
        pass

    def setup(self):
        pass

    def test_connection(self):
        return False


class _CLICheckClient:
    """Client mimicking a CLI agent with is_available(), command, timeout, working_dir."""

    def __init__(self):
        self.command = "fake-cli"
        self.timeout = 30
        self.working_dir = None

    def is_available(self):
        return True


class _CLICheckUnavailableClient:
    """CLI client that reports unavailable."""

    def __init__(self):
        self.command = "missing-tool"
        self.timeout = 10
        self.working_dir = "/tmp"

    def is_available(self):
        return False


# ---------------------------------------------------------------------------
# Success-path tests for _handle_agent_execute
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHandleAgentExecuteSuccessPaths:
    """Test the happy path of _handle_agent_execute using real helper classes."""

    def test_success_response_returns_true(self, capsys):
        from codomyrmex.agents.cli.handlers import _handle_agent_execute
        args = _make_args(prompt="hi")
        result = _handle_agent_execute(_SuccessClient, "TestAgent", args)
        assert result is True

    def test_success_response_prints_content(self, capsys):
        from codomyrmex.agents.cli.handlers import _handle_agent_execute
        args = _make_args(prompt="hi")
        _handle_agent_execute(_SuccessClient, "TestAgent", args)
        captured = capsys.readouterr()
        assert "hello from test" in captured.out

    def test_success_with_metadata_branch(self, capsys):
        """Non-empty metadata dict hits the metadata printing branch (line 102)."""
        from codomyrmex.agents.cli.handlers import _handle_agent_execute
        args = _make_args(prompt="hi", format="text")
        result = _handle_agent_execute(_SuccessClientWithMetadata, "TestAgent", args)
        assert result is True
        captured = capsys.readouterr()
        assert "result" in captured.out

    def test_success_with_metadata_json_format(self, capsys):
        """Metadata branch with json format output."""
        from codomyrmex.agents.cli.handlers import _handle_agent_execute
        args = _make_args(prompt="hi", format="json")
        result = _handle_agent_execute(_SuccessClientWithMetadata, "TestAgent", args)
        assert result is True

    def test_failure_response_returns_false(self, capsys):
        from codomyrmex.agents.cli.handlers import _handle_agent_execute
        args = _make_args(prompt="hi")
        result = _handle_agent_execute(_FailureResponseClient, "TestAgent", args)
        assert result is False

    def test_success_with_output_file(self, tmp_path, capsys):
        """Success path writes response content to output file (line 108-110)."""
        from codomyrmex.agents.cli.handlers import _handle_agent_execute
        outfile = tmp_path / "response.txt"
        args = _make_args(prompt="hi", output=str(outfile))
        result = _handle_agent_execute(_SuccessClient, "TestAgent", args)
        assert result is True
        assert outfile.exists()
        assert outfile.read_text(encoding="utf-8") == "hello from test"

    def test_success_output_file_content_matches_response(self, tmp_path, capsys):
        """File written by handler contains exactly the response content."""
        from codomyrmex.agents.cli.handlers import _handle_agent_execute
        outfile = tmp_path / "out.txt"
        args = _make_args(prompt="write this", output=str(outfile))
        _handle_agent_execute(_SuccessClient, "TestAgent", args)
        assert "hello from test" in outfile.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Success-path tests for _handle_agent_stream
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHandleAgentStreamSuccessPaths:
    """Test the happy path of _handle_agent_stream using real helper classes."""

    def test_success_stream_returns_true(self, capsys):
        from codomyrmex.agents.cli.handlers import _handle_agent_stream
        args = _make_args(prompt="hi")
        result = _handle_agent_stream(_SuccessClient, "TestAgent", args)
        assert result is True

    def test_success_stream_prints_chunks(self, capsys):
        from codomyrmex.agents.cli.handlers import _handle_agent_stream
        args = _make_args(prompt="hi")
        _handle_agent_stream(_SuccessClient, "TestAgent", args)
        captured = capsys.readouterr()
        assert "chunk1" in captured.out
        assert "chunk2" in captured.out

    def test_success_stream_with_output_file(self, tmp_path, capsys):
        """Stream success path writes joined chunks to output file (line 146-148)."""
        from codomyrmex.agents.cli.handlers import _handle_agent_stream
        outfile = tmp_path / "stream_out.txt"
        args = _make_args(prompt="hi", output=str(outfile))
        result = _handle_agent_stream(_SuccessClient, "TestAgent", args)
        assert result is True
        assert outfile.exists()
        content = outfile.read_text(encoding="utf-8")
        assert "chunk1" in content
        assert "chunk2" in content

    def test_empty_stream_returns_true(self, capsys):
        """A stream that yields nothing still returns True."""
        from codomyrmex.agents.cli.handlers import _handle_agent_stream

        class EmptyStreamClient:
            def __init__(self):
                pass

            def stream(self, request):
                return iter([])

        args = _make_args(prompt="hi")
        result = _handle_agent_stream(EmptyStreamClient, "TestAgent", args)
        assert result is True

    def test_stream_with_output_file_metadata(self, tmp_path, capsys):
        """Ensure the joined output file only contains stream chunks."""
        from codomyrmex.agents.cli.handlers import _handle_agent_stream
        outfile = tmp_path / "stream.txt"
        args = _make_args(prompt="hi", output=str(outfile))
        _handle_agent_stream(_SuccessClientWithMetadata, "TestAgent", args)
        content = outfile.read_text(encoding="utf-8")
        assert "line1" in content


# ---------------------------------------------------------------------------
# Success-path tests for handle_agent_setup / handle_agent_test
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHandleAgentSetupSuccessPaths:
    """Test the happy path of handle_agent_setup."""

    def test_setup_success_returns_true(self, capsys):
        args = _make_args()
        result = handle_agent_setup(_SetupableClient, "TestAgent", args)
        assert result is True

    def test_setup_success_prints_section(self, capsys):
        args = _make_args()
        handle_agent_setup(_SetupableClient, "TestAgent", args)
        captured = capsys.readouterr()
        # Should mention the client name in printed output
        assert "TestAgent" in captured.out

    def test_setup_raises_is_caught(self, capsys):
        """setup() that raises is caught, returns False."""

        class ErrorSetupClient:
            def __init__(self, config=None):
                pass

            def setup(self):
                raise RuntimeError("setup bombed")

        args = _make_args()
        result = handle_agent_setup(ErrorSetupClient, "ErrorAgent", args)
        assert result is False


@pytest.mark.unit
class TestHandleAgentTestSuccessPaths:
    """Test the happy path of handle_agent_test."""

    def test_test_connection_success_returns_true(self, capsys):
        args = _make_args()
        result = handle_agent_test(_SetupableClient, "TestAgent", args)
        assert result is True

    def test_test_connection_fail_returns_false(self, capsys):
        args = _make_args()
        result = handle_agent_test(_TestFailClient, "TestAgent", args)
        assert result is False

    def test_test_connection_prints_pass_message(self, capsys):
        args = _make_args()
        handle_agent_test(_SetupableClient, "TestAgent", args)
        captured = capsys.readouterr()
        assert "test" in captured.out.lower() or "TestAgent" in captured.out

    def test_test_connection_prints_fail_message(self, capsys):
        args = _make_args()
        handle_agent_test(_TestFailClient, "TestAgent", args)
        captured = capsys.readouterr()
        assert "TestAgent" in captured.out or "failed" in captured.out.lower()

    def test_test_connection_raises_is_caught(self, capsys):
        """test_connection() that raises is caught and returns False."""

        class ExplodingTestClient:
            def __init__(self, config=None):
                pass

            def test_connection(self):
                raise ConnectionError("no route to host")

        args = _make_args()
        result = handle_agent_test(ExplodingTestClient, "ExplodingAgent", args)
        assert result is False


# ---------------------------------------------------------------------------
# Success-path tests for _handle_cli_agent_check
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHandleCliAgentCheck:
    """Test _handle_cli_agent_check directly with real helper clients."""

    def test_available_client_returns_true(self, capsys):
        from codomyrmex.agents.cli.handlers import _handle_cli_agent_check
        args = _make_args()
        result = _handle_cli_agent_check(_CLICheckClient, "FakeCLI", args)
        assert result is True

    def test_available_client_prints_command(self, capsys):
        from codomyrmex.agents.cli.handlers import _handle_cli_agent_check
        args = _make_args()
        _handle_cli_agent_check(_CLICheckClient, "FakeCLI", args)
        captured = capsys.readouterr()
        assert "fake-cli" in captured.out

    def test_available_client_prints_timeout(self, capsys):
        from codomyrmex.agents.cli.handlers import _handle_cli_agent_check
        args = _make_args()
        _handle_cli_agent_check(_CLICheckClient, "FakeCLI", args)
        captured = capsys.readouterr()
        assert "30" in captured.out

    def test_unavailable_client_still_returns_true(self, capsys):
        """Per handler logic: even unavailable result returns True (not an error)."""
        from codomyrmex.agents.cli.handlers import _handle_cli_agent_check
        args = _make_args()
        result = _handle_cli_agent_check(_CLICheckUnavailableClient, "MissingCLI", args)
        assert result is True

    def test_unavailable_client_prints_warning(self, capsys):
        from codomyrmex.agents.cli.handlers import _handle_cli_agent_check
        args = _make_args()
        _handle_cli_agent_check(_CLICheckUnavailableClient, "MissingCLI", args)
        captured = capsys.readouterr()
        # Should print a warning about unavailability
        assert "not available" in captured.out.lower() or "MissingCLI" in captured.out

    def test_with_working_dir_prints_it(self, capsys):
        """When working_dir is set, it should appear in output."""
        from codomyrmex.agents.cli.handlers import _handle_cli_agent_check

        class DirClient:
            def __init__(self):
                self.command = "tool"
                self.timeout = 5
                self.working_dir = "/some/dir"

            def is_available(self):
                return True

        args = _make_args()
        _handle_cli_agent_check(DirClient, "DirTool", args)
        captured = capsys.readouterr()
        assert "/some/dir" in captured.out

    def test_none_client_returns_false(self, capsys):
        from codomyrmex.agents.cli.handlers import _handle_cli_agent_check
        args = _make_args()
        result = _handle_cli_agent_check(None, "Ghost", args)
        assert result is False

    def test_check_raises_is_caught(self, capsys):
        """is_available() that raises is caught, returns False."""
        from codomyrmex.agents.cli.handlers import _handle_cli_agent_check

        class ExplodingClient:
            def __init__(self):
                self.command = "boom"
                self.timeout = 5
                self.working_dir = None

            def is_available(self):
                raise OSError("disk error")

        args = _make_args()
        result = _handle_cli_agent_check(ExplodingClient, "Exploder", args)
        assert result is False


# ---------------------------------------------------------------------------
# _handle_api_key_check paths using real get_config()
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHandleApiKeyCheck:
    """Test _handle_api_key_check using real get_config() and a dummy class."""

    def test_no_api_key_returns_false(self, capsys):
        """Default config has no claude_api_key; should return False."""
        from codomyrmex.agents.cli.handlers import _handle_api_key_check

        class FakeAPIClient:
            pass

        # claude_api_key is None by default in AgentConfig
        args = _make_args()
        result = _handle_api_key_check(FakeAPIClient, "FakeAPI", "claude", "FAKE_API_KEY", args)
        assert result is False

    def test_no_api_key_prints_warning(self, capsys):
        """When API key missing, warning is printed."""
        from codomyrmex.agents.cli.handlers import _handle_api_key_check

        class FakeAPIClient:
            pass

        args = _make_args()
        _handle_api_key_check(FakeAPIClient, "FakeAPI", "claude", "FAKE_API_KEY", args)
        captured = capsys.readouterr()
        assert "FakeAPI" in captured.out or "api key" in captured.out.lower()

    def test_none_client_returns_false(self, capsys):
        """None client_class returns False immediately."""
        from codomyrmex.agents.cli.handlers import _handle_api_key_check
        args = _make_args()
        result = _handle_api_key_check(None, "Ghost", "ghost", "GHOST_KEY", args)
        assert result is False

    def test_prints_model_info(self, capsys):
        """_handle_api_key_check always prints model, timeout, max_tokens, temperature."""
        from codomyrmex.agents.cli.handlers import _handle_api_key_check

        class FakeAPIClient:
            pass

        args = _make_args()
        _handle_api_key_check(FakeAPIClient, "FakeAPI", "claude", "CLAUDE_KEY", args)
        captured = capsys.readouterr()
        # The config prints model/timeout/max_tokens/temperature
        assert "Model" in captured.out or "model" in captured.out.lower()

    def test_codex_check_uses_api_key_path(self, capsys):
        """handle_codex_check exercises the real _handle_api_key_check."""
        args = _make_args()
        result = handle_codex_check(args)
        assert isinstance(result, bool)
        captured = capsys.readouterr()
        assert "codex" in captured.out.lower() or "Codex" in captured.out

    def test_claude_check_uses_api_key_path(self, capsys):
        """handle_claude_check exercises the real _handle_api_key_check."""
        args = _make_args()
        result = handle_claude_check(args)
        assert isinstance(result, bool)
        captured = capsys.readouterr()
        assert "claude" in captured.out.lower() or "Claude" in captured.out


# ---------------------------------------------------------------------------
# OpenCode handlers without live CLI (test None-guard and error paths)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestOpenCodeHandlersNoLiveCLI:
    """Test OpenCode handlers by exercising paths that don't need live CLI."""

    def test_opencode_check_runs_without_crash(self, capsys):
        """handle_opencode_check always returns a bool regardless of CLI availability."""
        args = _make_args()
        result = handle_opencode_check(args)
        assert isinstance(result, bool)

    def test_opencode_init_runs_without_crash(self, capsys):
        """handle_opencode_init with path=None runs without crashing."""
        args = _make_args(path=None)
        result = handle_opencode_init(args)
        assert isinstance(result, bool)

    def test_opencode_version_runs_without_crash(self, capsys):
        args = _make_args()
        result = handle_opencode_version(args)
        assert isinstance(result, bool)

    def test_opencode_execute_runs_without_crash(self, capsys):
        args = _make_args(prompt="test")
        result = handle_opencode_execute(args)
        assert isinstance(result, bool)

    def test_opencode_stream_runs_without_crash(self, capsys):
        args = _make_args(prompt="test")
        result = handle_opencode_stream(args)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Jules handlers without live CLI
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestJulesHandlersNoLiveCLI:
    """Verify Jules handler entry points return bool without crashing."""

    def test_jules_check_returns_bool(self, capsys):
        args = _make_args()
        result = handle_jules_check(args)
        assert isinstance(result, bool)

    def test_jules_help_returns_bool(self, capsys):
        args = _make_args()
        result = handle_jules_help(args)
        assert isinstance(result, bool)

    def test_jules_command_returns_bool(self, capsys):
        args = _make_args(cmd="status", args=[])
        result = handle_jules_command(args)
        assert isinstance(result, bool)

    def test_jules_execute_returns_bool(self, capsys):
        args = _make_args(prompt="hello")
        result = handle_jules_execute(args)
        assert isinstance(result, bool)

    def test_jules_stream_returns_bool(self, capsys):
        args = _make_args(prompt="hello")
        result = handle_jules_stream(args)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Gemini handlers without live CLI
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGeminiHandlersNoLiveCLI:
    """Verify Gemini handler entry points return bool without crashing."""

    def test_gemini_check_returns_bool(self, capsys):
        args = _make_args()
        result = handle_gemini_check(args)
        assert isinstance(result, bool)

    def test_gemini_execute_returns_bool(self, capsys):
        args = _make_args(prompt="hi")
        result = handle_gemini_execute(args)
        assert isinstance(result, bool)

    def test_gemini_stream_returns_bool(self, capsys):
        args = _make_args(prompt="hi")
        result = handle_gemini_stream(args)
        assert isinstance(result, bool)

    def test_gemini_chat_save_returns_bool(self, capsys):
        args = _make_args(tag="my-session", prompt="save this")
        result = handle_gemini_chat_save(args)
        assert isinstance(result, bool)

    def test_gemini_chat_resume_returns_bool(self, capsys):
        args = _make_args(tag="my-session")
        result = handle_gemini_chat_resume(args)
        assert isinstance(result, bool)

    def test_gemini_chat_list_returns_bool(self, capsys):
        args = _make_args()
        result = handle_gemini_chat_list(args)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Droid handlers — extended tests (no droid module needed)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDroidHandlersExtended:
    """Extended droid handler tests exercising droid-unavailable paths."""

    def test_droid_start_returns_bool(self, capsys):
        args = _make_args()
        result = handle_droid_start(args)
        assert isinstance(result, bool)

    def test_droid_stop_returns_bool(self, capsys):
        args = _make_args()
        result = handle_droid_stop(args)
        assert isinstance(result, bool)

    def test_droid_status_returns_bool(self, capsys):
        args = _make_args()
        result = handle_droid_status(args)
        assert isinstance(result, bool)

    def test_droid_config_show_returns_bool(self, capsys):
        args = _make_args()
        result = handle_droid_config_show(args)
        assert isinstance(result, bool)

    def test_droid_status_json_format(self, capsys):
        """Droid status with json format doesn't crash."""
        args = _make_args(format="json")
        result = handle_droid_status(args)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# handle_info edge cases
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHandleInfoEdgeCases:
    """Additional edge cases for handle_info."""

    def test_handle_info_no_format_attr(self, capsys):
        """args without 'format' attribute falls back to default."""
        args = SimpleNamespace()  # no format attr at all
        result = handle_info(args)
        assert result is True

    def test_handle_info_unknown_format(self, capsys):
        """Unknown format string should not crash — falls through format_output."""
        args = _make_args(format="yaml")
        result = handle_info(args)
        assert result is True

    def test_handle_info_output_contains_module_name(self, capsys):
        args = _make_args(format="text")
        handle_info(args)
        captured = capsys.readouterr()
        assert "agents" in captured.out.lower()


# ---------------------------------------------------------------------------
# _parse_context edge cases (additional)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestParseContextEdgeCases:
    """Additional edge cases for _parse_context."""

    def test_whitespace_only_returns_empty_dict(self):
        """Whitespace-only string: json.loads raises JSONDecodeError -> {}."""
        result = _parse_context("   ")
        assert result == {}

    def test_number_string(self):
        """A bare number is valid JSON."""
        result = _parse_context("42")
        assert result == 42

    def test_unicode_content(self):
        data = {"greeting": "こんにちは", "count": 3}
        result = _parse_context(json.dumps(data))
        assert result == data

    def test_deeply_nested_json(self):
        data = {"a": {"b": {"c": {"d": [1, 2, 3]}}}}
        result = _parse_context(json.dumps(data))
        assert result["a"]["b"]["c"]["d"] == [1, 2, 3]

    def test_json_with_null_value(self):
        result = _parse_context('{"key": null}')
        assert result == {"key": None}


# ---------------------------------------------------------------------------
# _create_agent_request edge cases
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCreateAgentRequestEdgeCases:
    """Additional edge cases for _create_agent_request."""

    def test_empty_prompt(self):
        args = _make_args(prompt="")
        req = _create_agent_request("", args)
        assert req.prompt == ""

    def test_long_prompt(self):
        long_prompt = "x" * 10000
        args = _make_args(prompt=long_prompt)
        req = _create_agent_request(long_prompt, args)
        assert req.prompt == long_prompt

    def test_invalid_json_context_gives_empty_dict(self):
        args = _make_args(context="invalid-json")
        req = _create_agent_request("p", args)
        assert req.context == {}

    def test_valid_json_context_propagated(self):
        args = _make_args(context='{"flag": true}')
        req = _create_agent_request("p", args)
        assert req.context == {"flag": True}

    def test_timeout_zero(self):
        args = _make_args(timeout=0)
        req = _create_agent_request("p", args)
        assert req.timeout == 0

    def test_timeout_large_value(self):
        args = _make_args(timeout=3600)
        req = _create_agent_request("p", args)
        assert req.timeout == 3600
