"""Tests for HermesClient execution logic (zero-mock).

These tests run real subprocesses against a fake shim binary in $PATH
to achieve 100% real code coverage of the execution methods without hitting real APIs.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.hermes.hermes_client import HermesClient, HermesError


class TestHermesClientExecutionShims:
    """Verify hermes_client.py execution logic using subprocess shims."""

    @pytest.fixture
    def shim_bin_dir(self, tmp_path: Path, monkeypatch) -> Path:
        """Create a temporary directory for shim binaries and add it to PATH."""
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ.get('PATH', '')}")
        return bin_dir

    def test_execute_via_cli_success(self, shim_bin_dir: Path) -> None:
        """Test _execute_via_cli with a successful shim."""
        hermes_bin = shim_bin_dir / "hermes"
        # Mimic Hermes CLI outputting a plain response
        hermes_bin.write_text("#!/bin/sh\necho 'Hello from shim'\nexit 0\n")
        hermes_bin.chmod(hermes_bin.stat().st_mode | stat.S_IEXEC)

        client = HermesClient(config={"yolo": True})
        req = AgentRequest(prompt="test prompt")
        # Ensure client knows CLI is "available"
        client._active_backend = "cli"

        result = client._execute_via_cli(req)
        assert result.is_success()
        assert result.content.strip() == "Hello from shim"
        assert result.metadata["backend"] == "cli"

    def test_execute_via_cli_failure(self, shim_bin_dir: Path) -> None:
        """Test _execute_via_cli with a failing shim."""
        hermes_bin = shim_bin_dir / "hermes"
        hermes_bin.write_text("#!/bin/sh\necho 'API Error 401' >&2\nexit 1\n")
        hermes_bin.chmod(hermes_bin.stat().st_mode | stat.S_IEXEC)

        client = HermesClient()
        client._active_backend = "cli"
        req = AgentRequest(prompt="test prompt")

        with pytest.raises(HermesError) as exc:
            client._execute_via_cli(req)
        assert "API Error 401" in str(exc.value)

    def test_execute_via_ollama_success(self, shim_bin_dir: Path) -> None:
        """Test _execute_via_ollama with a successful shim."""
        ollama_bin = shim_bin_dir / "ollama"
        ollama_bin.write_text("#!/bin/sh\necho 'Local model response'\nexit 0\n")
        ollama_bin.chmod(ollama_bin.stat().st_mode | stat.S_IEXEC)

        client = HermesClient(config={"hermes_model": "hermes3"})
        req = AgentRequest(prompt="test prompt")

        result = client._execute_via_ollama(req)
        assert result.is_success()
        assert "Local model response" in result.content
        assert result.metadata["backend"] == "ollama"

    def test_execute_via_ollama_failure(self, shim_bin_dir: Path) -> None:
        """Test _execute_via_ollama with a failing shim."""
        ollama_bin = shim_bin_dir / "ollama"
        ollama_bin.write_text("#!/bin/sh\necho 'Model not found' >&2\nexit 1\n")
        ollama_bin.chmod(ollama_bin.stat().st_mode | stat.S_IEXEC)

        client = HermesClient()
        req = AgentRequest(prompt="test prompt")

        with pytest.raises(HermesError) as exc:
            client._execute_via_ollama(req)
        assert "Model not found" in str(exc.value)

    def test_execute_primary_fallback(self, shim_bin_dir: Path) -> None:
        """Test that HermesClient falls back to Ollama if CLI returns rate limit."""
        hermes_bin = shim_bin_dir / "hermes"
        # Return 429 Rate Limit which triggers fallback
        hermes_bin.write_text("#!/bin/sh\necho 'Rate limit exceeded' >&2\nexit 1\n")
        hermes_bin.chmod(hermes_bin.stat().st_mode | stat.S_IEXEC)

        ollama_bin = shim_bin_dir / "ollama"
        ollama_bin.write_text("#!/bin/sh\necho 'Fallback success'\nexit 0\n")
        ollama_bin.chmod(ollama_bin.stat().st_mode | stat.S_IEXEC)

        # Require a monkeypatch for _is_cli_configured so it tries CLI first
        client = HermesClient(config={
            "fallback_model": "hermes3-fallback",
        })
        client._active_backend = "cli"
        # Bypass the api key check to let it try to run CLI
        client._is_cli_configured = lambda: True

        req = AgentRequest(prompt="test prompt")

        # This will call _execute_impl which catches HermesError, sees "rate limit",
        # and falls back to Ollama.
        result = client._execute_impl(req)
        assert result.is_success()
        assert "Fallback success" in result.content
        assert result.metadata["backend"] == "ollama"
        assert result.metadata["is_fallback"] is True
        assert result.metadata["model"] == "hermes3-fallback"

    def test_stream_via_ollama(self, shim_bin_dir: Path) -> None:
        """Test _stream_via_ollama yields chunks."""
        ollama_bin = shim_bin_dir / "ollama"
        ollama_bin.write_text("#!/bin/sh\necho 'stream 1'\nsleep 0.1\necho 'stream 2'\nexit 0\n")
        ollama_bin.chmod(ollama_bin.stat().st_mode | stat.S_IEXEC)

        client = HermesClient()
        req = AgentRequest(prompt="test prompt")
        chunks = list(client._stream_via_ollama(req))

        assert "stream 1" in chunks
        assert "stream 2" in chunks

    def test_chat_session_simple_reply(self, shim_bin_dir: Path, tmp_path: Path) -> None:
        """Test chat_session executes and updates database."""
        hermes_bin = shim_bin_dir / "hermes"
        hermes_bin.write_text("#!/bin/sh\necho 'Hello user!'\nexit 0\n")
        hermes_bin.chmod(hermes_bin.stat().st_mode | stat.S_IEXEC)

        db_path = tmp_path / "test_session.db"
        client = HermesClient(config={
            "hermes_session_db": str(db_path)
        })
        client._active_backend = "cli"
        client._is_cli_configured = lambda: True

        resp = client.chat_session("Hi there")
        assert resp.is_success()
        assert resp.content.strip() == "Hello user!"
        assert "session_id" in resp.metadata
