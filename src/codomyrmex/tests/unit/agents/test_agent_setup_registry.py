"""Unit tests for agents.agent_setup.registry — Zero-Mock compliant.

Covers: ProbeResult, AgentDescriptor, _probe_api_key_env, _probe_cli_binary,
_probe_ollama (offline path), AgentRegistry initialization and all public methods.
External network calls (Ollama, real APIs) are guarded with skipif.
"""

import os

import pytest

from codomyrmex.agents.agent_setup.registry import (
    AgentDescriptor,
    AgentRegistry,
    ProbeResult,
    _probe_api_key_env,
    _probe_cli_binary,
    _probe_ollama,
)

# ── ProbeResult ───────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestProbeResult:
    def test_operative_status(self):
        result = ProbeResult(name="test", status="operative", detail="ok")
        assert result.is_operative is True

    def test_key_missing_not_operative(self):
        result = ProbeResult(name="test", status="key_missing", detail="no key")
        assert result.is_operative is False

    def test_unreachable_not_operative(self):
        result = ProbeResult(name="test", status="unreachable", detail="timeout")
        assert result.is_operative is False

    def test_unavailable_not_operative(self):
        result = ProbeResult(name="test", status="unavailable", detail="missing binary")
        assert result.is_operative is False

    def test_latency_optional_defaults_none(self):
        result = ProbeResult(name="x", status="operative", detail="ok")
        assert result.latency_ms is None

    def test_latency_set(self):
        result = ProbeResult(name="x", status="operative", detail="ok", latency_ms=12.5)
        assert result.latency_ms == 12.5

    def test_name_stored(self):
        result = ProbeResult(name="ollama", status="operative", detail="up")
        assert result.name == "ollama"

    def test_detail_stored(self):
        detail = "Found at /usr/bin/gemini"
        result = ProbeResult(name="gemini", status="operative", detail=detail)
        assert result.detail == detail


# ── AgentDescriptor ───────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAgentDescriptor:
    def _make_descriptor(self, name: str = "test_agent") -> AgentDescriptor:
        return AgentDescriptor(
            name=name,
            display_name="Test Agent",
            agent_type="api",
            env_var="TEST_API_KEY",
            config_key="test_api_key",
            default_model="test-model",
            probe=lambda: ProbeResult(name=name, status="operative", detail="ok"),
        )

    def test_fields_stored(self):
        desc = self._make_descriptor("agent_x")
        assert desc.name == "agent_x"
        assert desc.display_name == "Test Agent"
        assert desc.agent_type == "api"
        assert desc.env_var == "TEST_API_KEY"
        assert desc.config_key == "test_api_key"
        assert desc.default_model == "test-model"

    def test_probe_callable_and_returns_probe_result(self):
        desc = self._make_descriptor("agent_y")
        result = desc.probe()
        assert isinstance(result, ProbeResult)
        assert result.name == "agent_y"

    def test_cli_type_descriptor(self):
        desc = AgentDescriptor(
            name="jules",
            display_name="Jules CLI",
            agent_type="cli",
            env_var="JULES_COMMAND",
            config_key="jules_command",
            default_model="n/a",
            probe=lambda: ProbeResult(name="jules", status="unavailable", detail="not found"),
        )
        assert desc.agent_type == "cli"

    def test_local_type_descriptor(self):
        desc = AgentDescriptor(
            name="ollama",
            display_name="Ollama",
            agent_type="local",
            env_var="OLLAMA_BASE_URL",
            config_key="ollama_base_url",
            default_model="llama3.2",
            probe=lambda: ProbeResult(name="ollama", status="unreachable", detail="no server"),
        )
        assert desc.agent_type == "local"


# ── _probe_api_key_env ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestProbeApiKeyEnv:
    def test_key_present_returns_operative(self):
        env_var = "CODOMYRMEX_TEST_KEY_PROBE_PRESENT"
        os.environ[env_var] = "sk-abcdefgh1234"
        try:
            result = _probe_api_key_env("test_agent", env_var)
            assert result.status == "operative"
            assert result.name == "test_agent"
            assert result.latency_ms is not None
            assert result.latency_ms >= 0
        finally:
            del os.environ[env_var]

    def test_key_present_detail_contains_prefix(self):
        env_var = "CODOMYRMEX_TEST_KEY_PROBE_PREFIX"
        os.environ[env_var] = "sk-12345678"
        try:
            result = _probe_api_key_env("myagent", env_var)
            # detail shows first 4 chars of key
            assert "sk-1" in result.detail
        finally:
            del os.environ[env_var]

    def test_key_missing_returns_key_missing_status(self):
        env_var = "CODOMYRMEX_TEST_KEY_PROBE_ABSENT_XYZ"
        if env_var in os.environ:
            del os.environ[env_var]
        result = _probe_api_key_env("test_agent", env_var)
        assert result.status == "key_missing"
        assert result.name == "test_agent"
        assert result.latency_ms is None

    def test_key_missing_detail_mentions_env_var(self):
        env_var = "CODOMYRMEX_PROBE_MISSING_DETAIL"
        if env_var in os.environ:
            del os.environ[env_var]
        result = _probe_api_key_env("myagent", env_var)
        assert env_var in result.detail

    def test_returns_probe_result_type(self):
        env_var = "CODOMYRMEX_TEST_PROBE_TYPE"
        if env_var in os.environ:
            del os.environ[env_var]
        result = _probe_api_key_env("agent", env_var)
        assert isinstance(result, ProbeResult)


# ── _probe_cli_binary ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestProbeCliBinary:
    def test_existing_binary_is_operative(self):
        # 'python3' or 'python' is guaranteed to be on PATH in test env
        import shutil

        binary = "python3" if shutil.which("python3") else "python"
        result = _probe_cli_binary("python_agent", binary)
        assert result.status == "operative"
        assert result.name == "python_agent"
        assert result.latency_ms is not None

    def test_existing_binary_detail_contains_path(self):
        import shutil

        binary = "python3" if shutil.which("python3") else "python"
        result = _probe_cli_binary("python_agent", binary)
        assert "Found at" in result.detail

    def test_nonexistent_binary_is_unavailable(self):
        result = _probe_cli_binary("ghost_agent", "this_binary_does_not_exist_xyzzy")
        assert result.status == "unavailable"
        assert result.name == "ghost_agent"

    def test_nonexistent_binary_detail_mentions_binary(self):
        binary = "binary_that_cannot_exist_in_path_xyz"
        result = _probe_cli_binary("ghost", binary)
        assert binary in result.detail

    def test_nonexistent_binary_latency_is_none(self):
        result = _probe_cli_binary("ghost", "no_such_binary_abc123")
        assert result.latency_ms is None

    def test_returns_probe_result_type(self):
        result = _probe_cli_binary("any", "echo")
        assert isinstance(result, ProbeResult)


# ── _probe_ollama (offline path) ──────────────────────────────────────────────


@pytest.mark.unit
class TestProbeOllamaOffline:
    def test_unreachable_server_returns_unreachable(self):
        # Use an invalid address that cannot possibly be reached
        result = _probe_ollama("http://127.0.0.1:1")
        assert result.status == "unreachable"
        assert result.name == "ollama"

    def test_unreachable_detail_contains_url(self):
        url = "http://127.0.0.1:1"
        result = _probe_ollama(url)
        assert url in result.detail

    def test_unreachable_latency_is_set(self):
        result = _probe_ollama("http://127.0.0.1:1")
        assert result.latency_ms is not None
        assert result.latency_ms >= 0

    def test_returns_probe_result_type(self):
        result = _probe_ollama("http://127.0.0.1:1")
        assert isinstance(result, ProbeResult)


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("OLLAMA_BASE_URL"),
    reason="OLLAMA_BASE_URL not set — skipping live Ollama probe",
)
class TestProbeOllamaLive:
    def test_live_ollama_probe_returns_probe_result(self):
        result = _probe_ollama(os.environ["OLLAMA_BASE_URL"])
        assert isinstance(result, ProbeResult)
        assert result.name == "ollama"
        assert result.status in ("operative", "unreachable")


# ── AgentRegistry ─────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAgentRegistryInit:
    def test_creates_without_error(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        assert registry is not None

    def test_list_agents_returns_non_empty_list(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        agents = registry.list_agents()
        assert isinstance(agents, list)
        assert len(agents) > 0

    def test_list_agents_all_are_descriptors(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        for agent in registry.list_agents():
            assert isinstance(agent, AgentDescriptor)

    def test_known_agents_present(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        names = {a.name for a in registry.list_agents()}
        # These must always be in the catalog
        for expected in ("claude", "codex", "deepseek", "ollama", "jules", "gemini"):
            assert expected in names, f"Expected '{expected}' in agent catalog"

    def test_each_agent_has_valid_type(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        valid_types = {"api", "cli", "local"}
        for desc in registry.list_agents():
            assert desc.agent_type in valid_types, (
                f"{desc.name} has invalid type '{desc.agent_type}'"
            )

    def test_each_agent_has_env_var(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        for desc in registry.list_agents():
            assert isinstance(desc.env_var, str)
            assert len(desc.env_var) > 0

    def test_list_agents_returns_independent_copy(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        a = registry.list_agents()
        b = registry.list_agents()
        assert a is not b  # independent lists


@pytest.mark.unit
class TestAgentRegistryProbeAgent:
    def test_probe_unknown_agent_returns_unavailable(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        result = registry.probe_agent("nonexistent_agent_xyz")
        assert result.status == "unavailable"
        assert result.name == "nonexistent_agent_xyz"
        assert "Unknown" in result.detail

    def test_probe_claude_returns_probe_result(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        result = registry.probe_agent("claude")
        assert isinstance(result, ProbeResult)
        assert result.name == "claude"
        # Without ANTHROPIC_API_KEY set: key_missing; with: operative
        assert result.status in ("operative", "key_missing")

    def test_probe_ollama_without_server_returns_unreachable(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        result = registry.probe_agent("ollama")
        assert isinstance(result, ProbeResult)
        assert result.name == "ollama"
        assert result.status == "unreachable"

    def test_probe_jules_without_binary_returns_unavailable_or_operative(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        result = registry.probe_agent("jules")
        assert isinstance(result, ProbeResult)
        assert result.status in ("operative", "unavailable")


@pytest.mark.unit
class TestAgentRegistryProbeAll:
    def test_probe_all_returns_list(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        results = registry.probe_all()
        assert isinstance(results, list)

    def test_probe_all_count_matches_catalog(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        results = registry.probe_all()
        assert len(results) == len(registry.list_agents())

    def test_probe_all_returns_only_probe_results(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        for result in registry.probe_all():
            assert isinstance(result, ProbeResult)

    def test_probe_all_valid_statuses(self):
        valid = {"operative", "key_missing", "unreachable", "unavailable"}
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        for result in registry.probe_all():
            assert result.status in valid, (
                f"{result.name} returned invalid status '{result.status}'"
            )


@pytest.mark.unit
class TestAgentRegistryGetOperative:
    def test_get_operative_returns_list(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        operative = registry.get_operative()
        assert isinstance(operative, list)

    def test_get_operative_names_are_strings(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        for name in registry.get_operative():
            assert isinstance(name, str)

    def test_get_operative_subset_of_catalog(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        catalog_names = {a.name for a in registry.list_agents()}
        for name in registry.get_operative():
            assert name in catalog_names

    @pytest.mark.skipif(
        bool(os.getenv("ANTHROPIC_API_KEY")),
        reason="ANTHROPIC_API_KEY is set — claude may be operative, test checks absent case",
    )
    def test_claude_not_operative_without_key(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        operative = registry.get_operative()
        assert "claude" not in operative


@pytest.mark.unit
class TestAgentRegistryOllamaBaseUrl:
    def test_uses_provided_url(self):
        registry = AgentRegistry(ollama_base_url="http://127.0.0.1:1")
        assert registry._ollama_base_url == "http://127.0.0.1:1"

    def test_falls_back_to_env_var(self):
        saved = os.environ.pop("OLLAMA_BASE_URL", None)
        try:
            os.environ["OLLAMA_BASE_URL"] = "http://localhost:11435"
            registry = AgentRegistry()
            assert registry._ollama_base_url == "http://localhost:11435"
        finally:
            if saved is not None:
                os.environ["OLLAMA_BASE_URL"] = saved
            else:
                os.environ.pop("OLLAMA_BASE_URL", None)
