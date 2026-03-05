"""Tests for codomyrmex.aider — core module, config, and exceptions."""

from __future__ import annotations

import os
import shutil

import pytest

from codomyrmex.aider import HAS_AIDER
from codomyrmex.aider.config import AiderConfig, get_config
from codomyrmex.aider.core import AiderRunner, get_aider_version
from codomyrmex.aider.exceptions import (
    AiderAPIKeyError,
    AiderError,
    AiderNotInstalledError,
    AiderTimeoutError,
)

# ---------------------------------------------------------------------------
# HAS_AIDER flag
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestHasAiderFlag:
    """Test the HAS_AIDER availability flag."""

    def test_has_aider_is_bool(self):
        """HAS_AIDER must be a plain bool."""
        assert isinstance(HAS_AIDER, bool)

    def test_has_aider_matches_shutil_which(self):
        """HAS_AIDER must agree with shutil.which('aider')."""
        expected = shutil.which("aider") is not None
        assert HAS_AIDER is expected


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestAiderExceptions:
    """Test the aider exception hierarchy."""

    def test_aider_error_is_exception(self):
        """AiderError must be a subclass of Exception."""
        assert issubclass(AiderError, Exception)

    def test_not_installed_is_aider_error(self):
        """AiderNotInstalledError must be a subclass of AiderError."""
        assert issubclass(AiderNotInstalledError, AiderError)

    def test_timeout_is_aider_error(self):
        """AiderTimeoutError must be a subclass of AiderError."""
        assert issubclass(AiderTimeoutError, AiderError)

    def test_api_key_is_aider_error(self):
        """AiderAPIKeyError must be a subclass of AiderError."""
        assert issubclass(AiderAPIKeyError, AiderError)

    def test_not_installed_can_be_caught_as_aider_error(self):
        """Catching AiderError must also catch AiderNotInstalledError."""
        with pytest.raises(AiderError):
            raise AiderNotInstalledError("test")

    def test_timeout_can_be_caught_as_aider_error(self):
        """Catching AiderError must also catch AiderTimeoutError."""
        with pytest.raises(AiderError):
            raise AiderTimeoutError("test")

    def test_api_key_can_be_caught_as_aider_error(self):
        """Catching AiderError must also catch AiderAPIKeyError."""
        with pytest.raises(AiderError):
            raise AiderAPIKeyError("test")

    def test_exception_message_preserved(self):
        """Exception must preserve the message string."""
        msg = "aider binary not found"
        exc = AiderNotInstalledError(msg)
        assert str(exc) == msg


# ---------------------------------------------------------------------------
# AiderConfig
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestAiderConfig:
    """Test AiderConfig dataclass and get_config()."""

    def test_default_model(self):
        """Default model should be claude-sonnet-4-6 when AIDER_MODEL not set."""
        saved = os.environ.pop("AIDER_MODEL", None)
        try:
            cfg = AiderConfig()
            assert cfg.model == "claude-sonnet-4-6"
        finally:
            if saved is not None:
                os.environ["AIDER_MODEL"] = saved

    def test_custom_model_from_env(self):
        """AIDER_MODEL env var should override the default model."""
        saved = os.environ.get("AIDER_MODEL")
        os.environ["AIDER_MODEL"] = "gpt-4o"
        try:
            cfg = AiderConfig()
            assert cfg.model == "gpt-4o"
        finally:
            if saved is not None:
                os.environ["AIDER_MODEL"] = saved
            else:
                os.environ.pop("AIDER_MODEL", None)

    def test_default_timeout(self):
        """Default timeout should be 300 when AIDER_TIMEOUT not set."""
        saved = os.environ.pop("AIDER_TIMEOUT", None)
        try:
            cfg = AiderConfig()
            assert cfg.timeout == 300
        finally:
            if saved is not None:
                os.environ["AIDER_TIMEOUT"] = saved

    def test_custom_timeout_from_env(self):
        """AIDER_TIMEOUT env var should override the default timeout."""
        saved = os.environ.get("AIDER_TIMEOUT")
        os.environ["AIDER_TIMEOUT"] = "600"
        try:
            cfg = AiderConfig()
            assert cfg.timeout == 600
        finally:
            if saved is not None:
                os.environ["AIDER_TIMEOUT"] = saved
            else:
                os.environ.pop("AIDER_TIMEOUT", None)

    def test_has_anthropic_key_true(self):
        """has_anthropic_key must be True when ANTHROPIC_API_KEY is set."""
        saved = os.environ.get("ANTHROPIC_API_KEY")
        os.environ["ANTHROPIC_API_KEY"] = "sk-test-key"
        try:
            cfg = AiderConfig()
            assert cfg.has_anthropic_key is True
        finally:
            if saved is not None:
                os.environ["ANTHROPIC_API_KEY"] = saved
            else:
                os.environ.pop("ANTHROPIC_API_KEY", None)

    def test_has_anthropic_key_false(self):
        """has_anthropic_key must be False when ANTHROPIC_API_KEY is empty."""
        saved = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            cfg = AiderConfig()
            assert cfg.has_anthropic_key is False
        finally:
            if saved is not None:
                os.environ["ANTHROPIC_API_KEY"] = saved

    def test_has_openai_key_true(self):
        """has_openai_key must be True when OPENAI_API_KEY is set."""
        saved = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
        try:
            cfg = AiderConfig()
            assert cfg.has_openai_key is True
        finally:
            if saved is not None:
                os.environ["OPENAI_API_KEY"] = saved
            else:
                os.environ.pop("OPENAI_API_KEY", None)

    def test_has_openai_key_false(self):
        """has_openai_key must be False when OPENAI_API_KEY is empty."""
        saved = os.environ.pop("OPENAI_API_KEY", None)
        try:
            cfg = AiderConfig()
            assert cfg.has_openai_key is False
        finally:
            if saved is not None:
                os.environ["OPENAI_API_KEY"] = saved

    def test_has_any_key_true_with_anthropic(self):
        """has_any_key must be True when at least anthropic key is set."""
        saved_a = os.environ.get("ANTHROPIC_API_KEY")
        saved_o = os.environ.pop("OPENAI_API_KEY", None)
        os.environ["ANTHROPIC_API_KEY"] = "sk-test"
        try:
            cfg = AiderConfig()
            assert cfg.has_any_key is True
        finally:
            if saved_a is not None:
                os.environ["ANTHROPIC_API_KEY"] = saved_a
            else:
                os.environ.pop("ANTHROPIC_API_KEY", None)
            if saved_o is not None:
                os.environ["OPENAI_API_KEY"] = saved_o

    def test_has_any_key_false_when_neither(self):
        """has_any_key must be False when no API keys are set."""
        saved_a = os.environ.pop("ANTHROPIC_API_KEY", None)
        saved_o = os.environ.pop("OPENAI_API_KEY", None)
        try:
            cfg = AiderConfig()
            assert cfg.has_any_key is False
        finally:
            if saved_a is not None:
                os.environ["ANTHROPIC_API_KEY"] = saved_a
            if saved_o is not None:
                os.environ["OPENAI_API_KEY"] = saved_o

    def test_get_config_returns_aider_config(self):
        """get_config() must return an AiderConfig instance."""
        cfg = get_config()
        assert isinstance(cfg, AiderConfig)


# ---------------------------------------------------------------------------
# AiderRunner — command building (no subprocess needed)
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestAiderRunnerBuildCmd:
    """Test AiderRunner._build_cmd() logic without running subprocesses."""

    @pytest.fixture
    def runner(self):
        """Create an AiderRunner with default settings."""
        return AiderRunner(model="test-model", timeout=60)

    @pytest.mark.skipif(shutil.which("aider") is None, reason="aider not installed")
    def test_build_cmd_includes_safe_flags(self, runner):
        """_build_cmd must always include --yes --no-pretty --no-auto-commits."""
        cmd = runner._build_cmd("fix bug", ["file.py"])
        assert "--yes" in cmd
        assert "--no-pretty" in cmd
        assert "--no-auto-commits" in cmd

    @pytest.mark.skipif(shutil.which("aider") is None, reason="aider not installed")
    def test_build_cmd_includes_model(self, runner):
        """_build_cmd must include --model with the configured model name."""
        cmd = runner._build_cmd("fix bug", ["file.py"])
        model_idx = cmd.index("--model")
        assert cmd[model_idx + 1] == "test-model"

    @pytest.mark.skipif(shutil.which("aider") is None, reason="aider not installed")
    def test_build_cmd_includes_message(self, runner):
        """_build_cmd must include --message with the instruction."""
        cmd = runner._build_cmd("fix the bug", ["file.py"])
        msg_idx = cmd.index("--message")
        assert cmd[msg_idx + 1] == "fix the bug"

    @pytest.mark.skipif(shutil.which("aider") is None, reason="aider not installed")
    def test_build_cmd_appends_files(self, runner):
        """_build_cmd must append file paths as positional arguments at the end."""
        cmd = runner._build_cmd("fix bug", ["a.py", "b.py"])
        assert cmd[-2] == "a.py"
        assert cmd[-1] == "b.py"

    @pytest.mark.skipif(shutil.which("aider") is None, reason="aider not installed")
    def test_build_cmd_ask_mode(self, runner):
        """_build_cmd with chat_mode='ask' must include --chat-mode ask."""
        cmd = runner._build_cmd("what does this do?", ["file.py"], chat_mode="ask")
        assert "--chat-mode" in cmd
        mode_idx = cmd.index("--chat-mode")
        assert cmd[mode_idx + 1] == "ask"

    @pytest.mark.skipif(shutil.which("aider") is None, reason="aider not installed")
    def test_build_cmd_code_mode_no_chat_mode_flag(self, runner):
        """_build_cmd with chat_mode='code' must NOT include --chat-mode flag."""
        cmd = runner._build_cmd("fix bug", ["file.py"], chat_mode="code")
        assert "--chat-mode" not in cmd

    @pytest.mark.skipif(shutil.which("aider") is None, reason="aider not installed")
    def test_build_cmd_editor_model(self, runner):
        """_build_cmd with editor_model must include --editor-model flag."""
        cmd = runner._build_cmd("refactor", ["file.py"], editor_model="gpt-4o")
        assert "--editor-model" in cmd
        editor_idx = cmd.index("--editor-model")
        assert cmd[editor_idx + 1] == "gpt-4o"


# ---------------------------------------------------------------------------
# AiderRunner — _find_aider error case
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
@pytest.mark.skipif(
    shutil.which("aider") is not None,
    reason="Only relevant when aider is NOT installed",
)
class TestAiderRunnerInstallCheck:
    """Test that _find_aider raises when aider is not in PATH."""

    def test_find_aider_raises_not_installed(self):
        """_find_aider must raise AiderNotInstalledError when aider is missing."""
        runner = AiderRunner()
        with pytest.raises(AiderNotInstalledError):
            runner._find_aider()


# ---------------------------------------------------------------------------
# get_aider_version
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestGetAiderVersion:
    """Tests for get_aider_version()."""

    def test_returns_string(self):
        """get_aider_version must always return a string."""
        result = get_aider_version()
        assert isinstance(result, str)

    @pytest.mark.skipif(shutil.which("aider") is None, reason="aider not installed")
    def test_returns_nonempty_when_installed(self):
        """get_aider_version must return a non-empty string when aider is installed."""
        result = get_aider_version()
        assert len(result) > 0

    @pytest.mark.skipif(
        shutil.which("aider") is not None,
        reason="Only relevant when aider is NOT installed",
    )
    def test_returns_empty_when_not_installed(self):
        """get_aider_version must return empty string when aider is not installed."""
        result = get_aider_version()
        assert result == ""


# ---------------------------------------------------------------------------
# AiderRunner — live subprocess tests (requires aider + API key)
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
@pytest.mark.skipif(
    shutil.which("aider") is None or not os.getenv("ANTHROPIC_API_KEY"),
    reason="aider not installed or ANTHROPIC_API_KEY not set",
)
@pytest.mark.slow
class TestAiderRunnerLive:
    """Live tests that actually invoke aider via subprocess."""

    def test_run_ask_returns_dict(self, tmp_path):
        """run_ask must return a dict with stdout, stderr, returncode keys."""
        test_file = tmp_path / "hello.py"
        test_file.write_text("print('hello')\n", encoding="utf-8")
        runner = AiderRunner(timeout=60)
        result = runner.run_ask([str(test_file)], "What does this file do?")
        assert isinstance(result, dict)
        assert "stdout" in result
        assert "stderr" in result
        assert "returncode" in result
