"""Comprehensive tests for agents.agent_setup.registry — zero-mock.

Covers: ProbeResult, AgentDescriptor, AgentRegistry (catalog building,
listing, probing, operative filtering).
"""

import pytest

from codomyrmex.agents.agent_setup.registry import (
    AgentDescriptor,
    AgentRegistry,
    ProbeResult,
)

# ---------------------------------------------------------------------------
# ProbeResult
# ---------------------------------------------------------------------------


class TestProbeResult:
    def test_operative_result(self):
        result = ProbeResult(name="claude", status="operative", detail="API key set")
        assert result.is_operative

    def test_non_operative_result(self):
        result = ProbeResult(name="claude", status="error", detail="No API key")
        assert not result.is_operative

    def test_with_latency(self):
        result = ProbeResult(
            name="ollama", status="ok", detail="Running", latency_ms=15.2
        )
        assert result.latency_ms == 15.2

    def test_default_latency_none(self):
        result = ProbeResult(name="test", status="ok", detail="ok")
        assert result.latency_ms is None


# ---------------------------------------------------------------------------
# AgentDescriptor
# ---------------------------------------------------------------------------


class TestAgentDescriptor:
    def test_create_descriptor(self):
        desc = AgentDescriptor(
            name="test_agent",
            display_name="Test Agent",
            agent_type="api",
            env_var="TEST_API_KEY",
            config_key="test",
            default_model="test-v1",
            probe=lambda: ProbeResult(name="test_agent", status="ok", detail="set"),
        )
        assert desc.name == "test_agent"
        assert desc.agent_type == "api"

    def test_probe_callable(self):
        desc = AgentDescriptor(
            name="test",
            display_name="Test",
            agent_type="local",
            env_var="TEST",
            config_key="test",
            default_model="v1",
            probe=lambda: ProbeResult(name="test", status="operative", detail="ok"),
        )
        result = desc.probe()
        assert isinstance(result, ProbeResult)
        assert result.is_operative


# ---------------------------------------------------------------------------
# AgentRegistry
# ---------------------------------------------------------------------------


class TestAgentRegistry:
    def test_init(self):
        registry = AgentRegistry()
        assert registry is not None

    def test_list_agents_returns_list(self):
        registry = AgentRegistry()
        agents = registry.list_agents()
        assert isinstance(agents, list)
        assert len(agents) > 0  # Should have at least some agents

    def test_all_agents_are_descriptors(self):
        registry = AgentRegistry()
        for agent in registry.list_agents():
            assert isinstance(agent, AgentDescriptor)

    def test_agent_names_unique(self):
        registry = AgentRegistry()
        names = [a.name for a in registry.list_agents()]
        assert len(names) == len(set(names))

    def test_probe_all_returns_list(self):
        registry = AgentRegistry()
        results = registry.probe_all()
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, ProbeResult)

    def test_probe_single_agent(self):
        registry = AgentRegistry()
        agents = registry.list_agents()
        if agents:
            result = registry.probe_agent(agents[0].name)
            assert isinstance(result, ProbeResult)
            assert result.name == agents[0].name

    def test_probe_unknown_agent(self):
        registry = AgentRegistry()
        # May return error ProbeResult instead of raising
        result = registry.probe_agent("nonexistent_agent_xyz")
        assert isinstance(result, ProbeResult)
        assert not result.is_operative

    def test_get_operative_returns_list(self):
        registry = AgentRegistry()
        operative = registry.get_operative()
        assert isinstance(operative, list)
        # All items should be strings (agent names)
        for name in operative:
            assert isinstance(name, str)
