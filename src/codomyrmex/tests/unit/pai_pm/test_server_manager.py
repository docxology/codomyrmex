"""Tests for PaiPmServerManager — always-running subset (no bun required)."""

from __future__ import annotations

import stat
from pathlib import Path

import pytest

from codomyrmex.pai_pm import HAS_BUN, PaiPmServerManager


@pytest.mark.unit
@pytest.mark.pai_pm
class TestPaiPmServerManagerBasic:
    """Tests that run regardless of bun availability."""

    def test_has_bun_is_bool(self) -> None:
        assert isinstance(HAS_BUN, bool)

    def test_instantiates_without_error(self) -> None:
        mgr = PaiPmServerManager()
        assert mgr is not None

    def test_is_running_returns_bool_when_server_down(self) -> None:
        mgr = PaiPmServerManager()
        # Redirect to a port that is guaranteed not listening
        mgr._cfg.port = 19997
        mgr._cfg.host = "127.0.0.1"
        result = mgr.is_running()
        assert isinstance(result, bool)
        assert result is False

    def test_is_running_never_raises(self) -> None:
        mgr = PaiPmServerManager()
        mgr._cfg.port = 19997
        # Must not raise any exception
        mgr.is_running()


@pytest.mark.unit
@pytest.mark.pai_pm
class TestPaiPmServerManagerPidFile:
    """PID file behavior — no bun required."""

    def test_write_pid_creates_file(self, tmp_path: Path) -> None:
        mgr = PaiPmServerManager()
        pid_file = tmp_path / "pai_pm.pid"
        # Temporarily redirect PID file path
        import codomyrmex.pai_pm.server_manager as sm

        original = sm._PID_FILE
        sm._PID_FILE = pid_file
        try:
            mgr._write_pid(12345)
            assert pid_file.exists()
        finally:
            sm._PID_FILE = original

    def test_write_pid_mode_0600(self, tmp_path: Path) -> None:
        mgr = PaiPmServerManager()
        pid_file = tmp_path / "pai_pm.pid"
        import codomyrmex.pai_pm.server_manager as sm

        original = sm._PID_FILE
        sm._PID_FILE = pid_file
        try:
            mgr._write_pid(12345)
            mode = stat.S_IMODE(pid_file.stat().st_mode)
            assert mode == 0o600, f"Expected 0o600, got {oct(mode)}"
        finally:
            sm._PID_FILE = original

    def test_read_pid_returns_correct_int(self, tmp_path: Path) -> None:
        mgr = PaiPmServerManager()
        pid_file = tmp_path / "pai_pm.pid"
        import codomyrmex.pai_pm.server_manager as sm

        original = sm._PID_FILE
        sm._PID_FILE = pid_file
        try:
            mgr._write_pid(99999)
            result = mgr._read_pid()
            assert result == 99999
        finally:
            sm._PID_FILE = original

    def test_read_pid_returns_none_when_missing(self, tmp_path: Path) -> None:
        mgr = PaiPmServerManager()
        import codomyrmex.pai_pm.server_manager as sm

        original = sm._PID_FILE
        sm._PID_FILE = tmp_path / "nonexistent.pid"
        try:
            result = mgr._read_pid()
            assert result is None
        finally:
            sm._PID_FILE = original


@pytest.mark.unit
@pytest.mark.pai_pm
class TestPaiPmSafeEnv:
    """_build_safe_env() must exclude API keys and include NO_COLOR."""

    def test_no_color_present(self) -> None:
        mgr = PaiPmServerManager()
        env = mgr._build_safe_env()
        assert env.get("NO_COLOR") == "1"

    def test_anthropic_api_key_excluded(self, monkeypatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        mgr = PaiPmServerManager()
        env = mgr._build_safe_env()
        assert "ANTHROPIC_API_KEY" not in env

    def test_openai_api_key_excluded(self, monkeypatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        mgr = PaiPmServerManager()
        env = mgr._build_safe_env()
        assert "OPENAI_API_KEY" not in env

    def test_pai_prefixed_vars_included(self, monkeypatch) -> None:
        monkeypatch.setenv("PAI_SOME_VAR", "myvalue")
        mgr = PaiPmServerManager()
        env = mgr._build_safe_env()
        assert env.get("PAI_SOME_VAR") == "myvalue"

    def test_path_included(self) -> None:
        mgr = PaiPmServerManager()
        env = mgr._build_safe_env()
        assert "PATH" in env
