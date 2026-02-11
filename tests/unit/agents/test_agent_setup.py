"""Zero-mock tests for agent_setup submodule.

Tests AgentDescriptor, ProbeResult, AgentRegistry, and config_file
using real objects — no mocks.
"""

import os
import tempfile
from pathlib import Path

import pytest

from codomyrmex.agents.agent_setup.registry import (
    AgentDescriptor,
    AgentRegistry,
    ProbeResult,
    _probe_api_key_env,
    _probe_cli_binary,
    _probe_ollama,
)
from codomyrmex.agents.agent_setup.config_file import (
    load_config,
    save_config,
    merge_with_env,
)


# ── ProbeResult ───────────────────────────────────────────────────────────

class TestProbeResult:
    def test_operative(self):
        r = ProbeResult(name="test", status="operative", detail="ok")
        assert r.is_operative

    def test_not_operative(self):
        for status in ("key_missing", "unreachable", "unavailable"):
            r = ProbeResult(name="test", status=status, detail="nope")
            assert not r.is_operative

    def test_latency(self):
        r = ProbeResult(name="x", status="operative", detail="ok", latency_ms=1.5)
        assert r.latency_ms == 1.5


# ── AgentDescriptor ──────────────────────────────────────────────────────

class TestAgentDescriptor:
    def test_fields(self):
        d = AgentDescriptor(
            name="test_agent",
            display_name="Test Agent",
            agent_type="api",
            env_var="TEST_KEY",
            config_key="test_api_key",
            default_model="test-v1",
            probe=lambda: ProbeResult(name="test_agent", status="operative", detail="ok"),
        )
        assert d.name == "test_agent"
        assert d.agent_type == "api"
        result = d.probe()
        assert result.is_operative


# ── Probe helpers (real checks) ──────────────────────────────────────────

class TestProbeHelpers:
    def test_api_key_env_missing(self):
        # Use a key guaranteed to not exist
        r = _probe_api_key_env("fake", "__CODOMYRMEX_NONEXISTENT_KEY__")
        assert r.status == "key_missing"

    def test_api_key_env_present(self):
        os.environ["__CODOMYRMEX_TEST_KEY__"] = "sk-test-1234"
        try:
            r = _probe_api_key_env("fake", "__CODOMYRMEX_TEST_KEY__")
            assert r.status == "operative"
            assert "sk-t" in r.detail
        finally:
            del os.environ["__CODOMYRMEX_TEST_KEY__"]

    def test_cli_binary_echo(self):
        """echo is a real binary available on all POSIX systems."""
        r = _probe_cli_binary("test", "echo")
        assert r.status == "operative"

    def test_cli_binary_missing(self):
        r = _probe_cli_binary("test", "__codomyrmex_nonexistent_binary__")
        assert r.status == "unavailable"

    def test_ollama_unreachable(self):
        """Probe against a port that definitely is not running Ollama."""
        r = _probe_ollama("http://127.0.0.1:19999")
        assert r.status == "unreachable"


# ── AgentRegistry ────────────────────────────────────────────────────────

class TestAgentRegistry:
    def test_list_agents(self):
        registry = AgentRegistry()
        agents = registry.list_agents()
        assert len(agents) == 11
        names = {a.name for a in agents}
        assert "claude" in names
        assert "ollama" in names

    def test_list_agents_types(self):
        registry = AgentRegistry()
        agents = registry.list_agents()
        types = {a.agent_type for a in agents}
        assert types == {"api", "cli", "local"}

    def test_probe_unknown_agent(self):
        registry = AgentRegistry()
        r = registry.probe_agent("nonexistent")
        assert r.status == "unavailable"
        assert r.name == "nonexistent"

    def test_probe_all_returns_results(self):
        registry = AgentRegistry()
        results = registry.probe_all()
        assert len(results) == 11
        for r in results:
            assert isinstance(r, ProbeResult)
            assert r.status in ("operative", "key_missing", "unreachable", "unavailable")

    def test_get_operative_returns_list(self):
        registry = AgentRegistry()
        operative = registry.get_operative()
        assert isinstance(operative, list)
        # At minimum echo-based test_cli_binary works, so some CLI agent might
        # or might not be operative depending on system; just check type
        for name in operative:
            assert isinstance(name, str)


# ── Config file ──────────────────────────────────────────────────────────

class TestConfigFile:
    def test_load_nonexistent(self):
        """Loading a missing file returns empty agents dict."""
        config = load_config("/tmp/__codomyrmex_no_such_file__.yaml")
        assert config == {"agents": {}}

    def test_save_and_load_roundtrip(self):
        data = {
            "agents": {
                "claude": {"api_key": "sk-ant-test", "model": "claude-3-opus"},
                "ollama": {"base_url": "http://localhost:11434"},
            }
        }
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            tmp_path = f.name

        try:
            save_config(data, tmp_path)
            loaded = load_config(tmp_path)
            assert loaded["agents"]["claude"]["api_key"] == "sk-ant-test"
            assert loaded["agents"]["ollama"]["base_url"] == "http://localhost:11434"

            # Check file permissions (unix only)
            if os.name != "nt":
                import stat
                mode = os.stat(tmp_path).st_mode & 0o777
                assert mode == 0o600
        finally:
            os.unlink(tmp_path)

    def test_merge_with_env(self):
        config = {
            "agents": {
                "claude": {"api_key": "sk-test", "model": "opus"},
                "ollama": {"base_url": "http://localhost:11434"},
            }
        }
        flat = merge_with_env(config)
        assert flat["claude_api_key"] == "sk-test"
        assert flat["claude_model"] == "opus"
        assert flat["ollama_base_url"] == "http://localhost:11434"
