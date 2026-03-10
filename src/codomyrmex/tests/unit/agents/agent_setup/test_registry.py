"""Tests for agents.agent_setup.registry — zero-mock policy compliant."""

from codomyrmex.agents.agent_setup.registry import (
    AgentDescriptor,
    AgentRegistry,
    ProbeResult,
    _probe_api_key_env,
    _probe_cli_binary,
)


class TestProbeResult:
    def test_operative_status(self):
        r = ProbeResult(name="test", status="operative", detail="ok")
        assert r.is_operative is True

    def test_key_missing_status(self):
        r = ProbeResult(name="test", status="key_missing", detail="missing")
        assert r.is_operative is False

    def test_unreachable_status(self):
        r = ProbeResult(name="test", status="unreachable", detail="down")
        assert r.is_operative is False

    def test_unavailable_status(self):
        r = ProbeResult(name="test", status="unavailable", detail="not found")
        assert r.is_operative is False

    def test_latency_ms_optional(self):
        r = ProbeResult(name="test", status="operative", detail="ok")
        assert r.latency_ms is None

    def test_latency_ms_set(self):
        r = ProbeResult(name="test", status="operative", detail="ok", latency_ms=12.5)
        assert r.latency_ms == 12.5

    def test_name_stored(self):
        r = ProbeResult(name="claude", status="operative", detail="ok")
        assert r.name == "claude"


class TestProbeApiKeyEnv:
    def test_key_present(self, monkeypatch):
        monkeypatch.setenv("TEST_API_KEY_XYZ", "sk-abcdefgh")
        result = _probe_api_key_env("testservice", "TEST_API_KEY_XYZ")
        assert result.status == "operative"
        assert result.name == "testservice"
        assert result.latency_ms is not None

    def test_key_absent(self, monkeypatch):
        monkeypatch.delenv("TEST_API_KEY_NOTSET", raising=False)
        result = _probe_api_key_env("testservice", "TEST_API_KEY_NOTSET")
        assert result.status == "key_missing"
        assert result.latency_ms is None

    def test_key_truncated_in_detail(self, monkeypatch):
        monkeypatch.setenv("MY_SECRET_KEY", "sk-abcdefghijklmn")
        result = _probe_api_key_env("svc", "MY_SECRET_KEY")
        assert "sk-a" in result.detail
        assert "abcdefghijklmn" not in result.detail  # truncated


class TestProbeCliBinary:
    def test_existing_binary(self):
        # 'python3' or 'python' is always available in test env
        binary = "python3"
        result = _probe_cli_binary("python", binary)
        # It may or may not be found — just check shape
        assert result.name == "python"
        assert result.status in ("operative", "unavailable")

    def test_nonexistent_binary(self):
        result = _probe_cli_binary("fakebinary999", "fakebinary999xyz_notreal")
        assert result.status == "unavailable"
        assert "fakebinary999xyz_notreal" in result.detail

    def test_found_binary_has_latency(self):
        result = _probe_cli_binary("sh", "sh")
        if result.status == "operative":
            assert result.latency_ms is not None


class TestAgentDescriptor:
    def test_basic_construction(self):
        desc = AgentDescriptor(
            name="myagent",
            display_name="My Agent",
            agent_type="api",
            env_var="MY_AGENT_KEY",
            config_key="my_agent_key",
            default_model="gpt-4",
            probe=lambda: ProbeResult(name="myagent", status="operative", detail="ok"),
        )
        assert desc.name == "myagent"
        assert desc.display_name == "My Agent"
        assert desc.agent_type == "api"
        assert desc.env_var == "MY_AGENT_KEY"

    def test_probe_callable(self):
        desc = AgentDescriptor(
            name="test",
            display_name="Test",
            agent_type="cli",
            env_var="TEST_BIN",
            config_key="test_bin",
            default_model="n/a",
            probe=lambda: ProbeResult(name="test", status="unavailable", detail="no"),
        )
        result = desc.probe()
        assert isinstance(result, ProbeResult)
        assert result.status == "unavailable"


class TestAgentRegistry:
    def test_list_agents_returns_descriptors(self):
        registry = AgentRegistry()
        agents = registry.list_agents()
        assert isinstance(agents, list)
        assert len(agents) > 0
        assert all(isinstance(a, AgentDescriptor) for a in agents)

    def test_list_agents_includes_claude(self):
        registry = AgentRegistry()
        names = [a.name for a in registry.list_agents()]
        assert "claude" in names

    def test_list_agents_includes_ollama(self):
        registry = AgentRegistry()
        names = [a.name for a in registry.list_agents()]
        assert "ollama" in names

    def test_list_agents_returns_copy(self):
        registry = AgentRegistry()
        agents1 = registry.list_agents()
        agents2 = registry.list_agents()
        # Should be independent copies
        assert agents1 is not agents2
        assert len(agents1) == len(agents2)

    def test_probe_unknown_agent(self):
        registry = AgentRegistry()
        result = registry.probe_agent("nonexistent_agent_xyz")
        assert result.status == "unavailable"
        assert result.name == "nonexistent_agent_xyz"

    def test_probe_agent_claude_key_absent(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        registry = AgentRegistry()
        result = registry.probe_agent("claude")
        assert result.name == "claude"
        assert result.status == "key_missing"

    def test_probe_agent_claude_key_present(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test123456")
        registry = AgentRegistry()
        result = registry.probe_agent("claude")
        assert result.status == "operative"

    def test_probe_all_returns_list(self):
        registry = AgentRegistry()
        results = registry.probe_all()
        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(r, ProbeResult) for r in results)

    def test_probe_all_count_matches_descriptors(self):
        registry = AgentRegistry()
        results = registry.probe_all()
        agents = registry.list_agents()
        assert len(results) == len(agents)

    def test_probe_all_handles_probe_error(self):
        registry = AgentRegistry()
        # Inject a descriptor that always raises
        bad_desc = AgentDescriptor(
            name="broken",
            display_name="Broken",
            agent_type="api",
            env_var="BROKEN_KEY",
            config_key="broken_key",
            default_model="n/a",
            probe=lambda: (_ for _ in ()).throw(RuntimeError("probe exploded")),
        )
        registry._descriptors.append(bad_desc)
        results = registry.probe_all()
        broken = next(r for r in results if r.name == "broken")
        assert broken.status == "unreachable"
        assert "probe exploded" in broken.detail

    def test_get_operative_returns_list_of_names(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test123")
        registry = AgentRegistry()
        operative = registry.get_operative()
        assert isinstance(operative, list)
        # With key set, claude should be operative
        assert "claude" in operative

    def test_get_operative_excludes_missing_keys(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        registry = AgentRegistry()
        operative = registry.get_operative()
        # Without API keys, API-type agents should not appear
        assert "claude" not in operative

    def test_ollama_url_from_env(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom-ollama:11434")
        registry = AgentRegistry()
        assert registry._ollama_base_url == "http://custom-ollama:11434"

    def test_default_ollama_url_when_env_unset(self, monkeypatch):
        monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
        registry = AgentRegistry()
        assert "11434" in registry._ollama_base_url or "localhost" in registry._ollama_base_url

    def test_all_descriptors_have_required_fields(self):
        registry = AgentRegistry()
        for desc in registry.list_agents():
            assert desc.name, "Agent descriptor missing name"
            assert desc.display_name, f"{desc.name}: missing display_name"
            assert desc.agent_type in ("api", "cli", "local"), f"{desc.name}: invalid type"
            assert desc.env_var, f"{desc.name}: missing env_var"
            assert callable(desc.probe), f"{desc.name}: probe not callable"
