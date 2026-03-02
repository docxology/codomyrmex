"""Zero-mock test suite for the PAI bridge module.

Tests real filesystem operations against the local PAI installation
at ``~/.claude/skills/PAI/``.  Also tests graceful degradation using
a temporary directory with no PAI content.

Upstream reference: https://github.com/danielmiessler/Personal_AI_Infrastructure
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codomyrmex.agents.pai import (
    ALGORITHM_PHASES,
    PAI_PRINCIPLES,
    PAI_UPSTREAM_URL,
    RESPONSE_DEPTH_LEVELS,
    PAIAgentInfo,
    PAIBridge,
    PAIConfig,
    PAIHookInfo,
    PAIMemoryStore,
    PAISkillInfo,
    PAIToolInfo,
)

# =====================================================================
# Fixtures
# =====================================================================


@pytest.fixture
def bridge() -> PAIBridge:
    """Bridge configured against real PAI installation."""
    return PAIBridge()


@pytest.fixture
def empty_bridge(tmp_path: Path) -> PAIBridge:
    """Bridge configured against a temp dir with NO PAI installation."""
    config = PAIConfig(
        pai_root=tmp_path / "nonexistent_pai",
        claude_root=tmp_path / "nonexistent_claude",
    )
    return PAIBridge(config=config)


# =====================================================================
# Module Exports
# =====================================================================


class TestModuleExports:
    """Verify that all public symbols are importable."""

    def test_bridge_importable(self) -> None:
        """Test functionality: bridge importable."""
        assert PAIBridge is not None

    def test_config_importable(self) -> None:
        """Test functionality: config importable."""
        assert PAIConfig is not None

    def test_dataclasses_importable(self) -> None:
        """Test functionality: dataclasses importable."""
        for cls in (PAISkillInfo, PAIToolInfo, PAIHookInfo, PAIAgentInfo, PAIMemoryStore):
            assert cls is not None

    def test_constants_importable(self) -> None:
        """Test functionality: constants importable."""
        assert len(ALGORITHM_PHASES) == 7
        assert len(RESPONSE_DEPTH_LEVELS) == 3
        assert len(PAI_PRINCIPLES) == 16
        assert PAI_UPSTREAM_URL.startswith("https://")


# =====================================================================
# Discovery & Status (Real PAI)
# =====================================================================


class TestDiscovery:
    """Test PAI discovery against the real installation."""

    def test_is_installed(self, bridge: PAIBridge) -> None:
        """Test functionality: is installed."""
        # PAI SKILL.md should exist on this machine
        assert bridge.is_installed() is True

    def test_get_status_structure(self, bridge: PAIBridge) -> None:
        """Test functionality: get status structure."""
        status = bridge.get_status()
        assert isinstance(status, dict)
        assert status["installed"] is True
        assert "pai_root" in status
        assert status["upstream"] == PAI_UPSTREAM_URL
        assert isinstance(status["components"], dict)

    def test_get_components(self, bridge: PAIBridge) -> None:
        """Test functionality: get components."""
        components = bridge.get_components()
        expected_keys = {"algorithm", "skills", "tools", "agents", "memory", "hooks", "security", "components"}
        assert expected_keys.issubset(set(components.keys()))

        # Each component has exists/count/path
        for _key, info in components.items():
            assert "exists" in info
            assert "count" in info
            assert "path" in info


# =====================================================================
# Algorithm Operations
# =====================================================================


class TestAlgorithm:
    """Test Algorithm phase and principle methods."""

    def test_phases_count(self) -> None:
        """Test functionality: phases count."""
        phases = PAIBridge.get_algorithm_phases()
        assert len(phases) == 7

    def test_phases_structure(self) -> None:
        """Test functionality: phases structure."""
        phases = PAIBridge.get_algorithm_phases()
        for phase in phases:
            assert "phase" in phase
            assert "name" in phase
            assert "description" in phase

    def test_phase_names(self) -> None:
        """Test functionality: phase names."""
        names = [p["name"] for p in PAIBridge.get_algorithm_phases()]
        assert names == ["OBSERVE", "THINK", "PLAN", "BUILD", "EXECUTE", "VERIFY", "LEARN"]

    def test_response_depth_levels(self) -> None:
        """Test functionality: response depth levels."""
        levels = PAIBridge.get_response_depth_levels()
        assert len(levels) == 3
        depth_names = [d["depth"] for d in levels]
        assert "FULL" in depth_names
        assert "MINIMAL" in depth_names

    def test_principles_count(self) -> None:
        """Test functionality: principles count."""
        assert len(PAIBridge.get_principles()) == 16

    def test_algorithm_version(self, bridge: PAIBridge) -> None:
        """Test functionality: algorithm version."""
        version = bridge.get_algorithm_version()
        # Should be a version string like "v0.2.25"
        assert version is not None
        assert version.startswith("v")


# =====================================================================
# Skill System
# =====================================================================


class TestSkills:
    """Test skill discovery against real PAI installation."""

    def test_list_skills_returns_list(self, bridge: PAIBridge) -> None:
        """Test functionality: list skills returns list."""
        skills = bridge.list_skills()
        assert isinstance(skills, list)
        assert len(skills) > 0

    def test_skill_info_structure(self, bridge: PAIBridge) -> None:
        """Test functionality: skill info structure."""
        skills = bridge.list_skills()
        for skill in skills:
            assert isinstance(skill, PAISkillInfo)
            assert isinstance(skill.name, str)
            assert isinstance(skill.path, str)
            assert isinstance(skill.file_count, int)
            assert skill.file_count >= 0

    def test_pai_skill_has_skill_md(self, bridge: PAIBridge) -> None:
        """The PAI skill pack itself should have a SKILL.md."""
        pai = bridge.get_skill_info("PAI")
        assert pai is not None
        assert pai.has_skill_md is True

    def test_get_skill_info_missing(self, bridge: PAIBridge) -> None:
        """Test functionality: get skill info missing."""
        result = bridge.get_skill_info("NonexistentSkill12345")
        assert result is None


# =====================================================================
# Tool System
# =====================================================================


class TestTools:
    """Test tool discovery against real PAI installation."""

    def test_list_tools_returns_list(self, bridge: PAIBridge) -> None:
        """Test functionality: list tools returns list."""
        tools = bridge.list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_tool_info_structure(self, bridge: PAIBridge) -> None:
        """Test functionality: tool info structure."""
        tools = bridge.list_tools()
        for tool in tools:
            assert isinstance(tool, PAIToolInfo)
            assert isinstance(tool.name, str)
            assert tool.size_bytes > 0

    def test_get_tool_info(self, bridge: PAIBridge) -> None:
        """Test functionality: get tool info."""
        # AddTask is a known tool from upstream
        tool = bridge.get_tool_info("AddTask")
        assert tool is not None
        assert tool.name == "AddTask"

    def test_get_tool_info_missing(self, bridge: PAIBridge) -> None:
        """Test functionality: get tool info missing."""
        assert bridge.get_tool_info("NonexistentTool12345") is None


# =====================================================================
# Hook System
# =====================================================================


class TestHooks:
    """Test hook discovery against real PAI installation."""

    def test_list_hooks_returns_list(self, bridge: PAIBridge) -> None:
        """Test functionality: list hooks returns list."""
        hooks = bridge.list_hooks()
        assert isinstance(hooks, list)
        assert len(hooks) > 0

    def test_hook_info_structure(self, bridge: PAIBridge) -> None:
        """Test functionality: hook info structure."""
        for hook in bridge.list_hooks():
            assert isinstance(hook, PAIHookInfo)
            assert isinstance(hook.name, str)
            assert isinstance(hook.is_archived, bool)

    def test_active_hooks_subset(self, bridge: PAIBridge) -> None:
        """Test functionality: active hooks subset."""
        all_hooks = bridge.list_hooks()
        active = bridge.list_active_hooks()
        assert len(active) <= len(all_hooks)
        for h in active:
            assert h.is_archived is False

    def test_get_hook_info(self, bridge: PAIBridge) -> None:
        """Test functionality: get hook info."""
        hook = bridge.get_hook_info("IntegrityCheck")
        assert hook is not None
        assert hook.name == "IntegrityCheck"


# =====================================================================
# Agent System
# =====================================================================


class TestAgents:
    """Test agent personality discovery."""

    def test_list_agents_returns_list(self, bridge: PAIBridge) -> None:
        """Test functionality: list agents returns list."""
        agents = bridge.list_agents()
        assert isinstance(agents, list)
        assert len(agents) > 0

    def test_agent_info_structure(self, bridge: PAIBridge) -> None:
        """Test functionality: agent info structure."""
        for agent in bridge.list_agents():
            assert isinstance(agent, PAIAgentInfo)
            assert isinstance(agent.name, str)
            assert agent.size_bytes > 0

    def test_known_agents_present(self, bridge: PAIBridge) -> None:
        """Test functionality: known agents present."""
        names = {a.name for a in bridge.list_agents()}
        # These are known upstream agent personalities
        expected = {"Engineer", "Architect", "Pentester"}
        assert expected.issubset(names), f"Missing agents: {expected - names}"

    def test_get_agent_info(self, bridge: PAIBridge) -> None:
        """Test functionality: get agent info."""
        agent = bridge.get_agent_info("Engineer")
        assert agent is not None


# =====================================================================
# Memory System
# =====================================================================


class TestMemory:
    """Test memory store discovery."""

    def test_list_memory_stores(self, bridge: PAIBridge) -> None:
        """Test functionality: list memory stores."""
        stores = bridge.list_memory_stores()
        assert isinstance(stores, list)
        assert len(stores) > 0

    def test_memory_store_structure(self, bridge: PAIBridge) -> None:
        """Test functionality: memory store structure."""
        for store in bridge.list_memory_stores():
            assert isinstance(store, PAIMemoryStore)
            assert isinstance(store.name, str)
            assert isinstance(store.item_count, int)

    def test_known_stores_present(self, bridge: PAIBridge) -> None:
        """Test functionality: known stores present."""
        names = {s.name for s in bridge.list_memory_stores()}
        expected = {"LEARNING", "STATE", "RESEARCH"}
        assert expected.issubset(names), f"Missing stores: {expected - names}"

    def test_get_memory_info(self, bridge: PAIBridge) -> None:
        """Test functionality: get memory info."""
        result = bridge.get_memory_info("LEARNING")
        assert result is not None
        assert result.name == "LEARNING"

    def test_get_memory_info_missing(self, bridge: PAIBridge) -> None:
        """Test functionality: get memory info missing."""
        assert bridge.get_memory_info("NonexistentStore12345") is None


# =====================================================================
# Security System
# =====================================================================


class TestSecurity:
    """Test security system discovery."""

    def test_security_config_structure(self, bridge: PAIBridge) -> None:
        """Test functionality: security config structure."""
        sec = bridge.get_security_config()
        assert isinstance(sec, dict)
        assert "exists" in sec
        assert "path" in sec
        assert "files" in sec
        assert isinstance(sec["files"], list)


# =====================================================================
# TELOS
# =====================================================================


class TestTelos:
    """Test TELOS identity file discovery."""

    def test_telos_returns_list(self, bridge: PAIBridge) -> None:
        """Test functionality: telos returns list."""
        files = bridge.get_telos_files()
        assert isinstance(files, list)


# =====================================================================
# Settings & MCP
# =====================================================================


class TestSettings:
    """Test settings and MCP registration."""

    def test_get_settings(self, bridge: PAIBridge) -> None:
        """Test functionality: get settings."""
        settings = bridge.get_settings()
        assert settings is not None
        assert isinstance(settings, dict)

    def test_get_pai_env(self, bridge: PAIBridge) -> None:
        """Test functionality: get pai env."""
        env = bridge.get_pai_env()
        assert isinstance(env, dict)
        # PAI_DIR is set in settings.json
        assert "PAI_DIR" in env

    def test_mcp_registration(self, bridge: PAIBridge) -> None:
        """Test functionality: mcp registration."""
        result = bridge.get_mcp_registration()
        # May or may not exist — just check the return type
        assert result is None or isinstance(result, dict)


# =====================================================================
# Graceful Degradation (No PAI Installed)
# =====================================================================


class TestGracefulDegradation:
    """Verify graceful behavior when PAI is NOT installed."""

    def test_not_installed(self, empty_bridge: PAIBridge) -> None:
        """Test functionality: not installed."""
        assert empty_bridge.is_installed() is False

    def test_status_when_absent(self, empty_bridge: PAIBridge) -> None:
        """Test functionality: status when absent."""
        status = empty_bridge.get_status()
        assert status["installed"] is False
        assert status["components"] == {}
        assert status["settings"] is None

    def test_list_skills_empty(self, empty_bridge: PAIBridge) -> None:
        """Test functionality: list skills empty."""
        assert empty_bridge.list_skills() == []

    def test_list_tools_empty(self, empty_bridge: PAIBridge) -> None:
        """Test functionality: list tools empty."""
        assert empty_bridge.list_tools() == []

    def test_list_hooks_empty(self, empty_bridge: PAIBridge) -> None:
        """Test functionality: list hooks empty."""
        assert empty_bridge.list_hooks() == []

    def test_list_agents_empty(self, empty_bridge: PAIBridge) -> None:
        """Test functionality: list agents empty."""
        assert empty_bridge.list_agents() == []

    def test_list_memory_empty(self, empty_bridge: PAIBridge) -> None:
        """Test functionality: list memory empty."""
        assert empty_bridge.list_memory_stores() == []

    def test_security_absent(self, empty_bridge: PAIBridge) -> None:
        """Test functionality: security absent."""
        sec = empty_bridge.get_security_config()
        assert sec["exists"] is False

    def test_telos_empty(self, empty_bridge: PAIBridge) -> None:
        """Test functionality: telos empty."""
        assert empty_bridge.get_telos_files() == []

    def test_algorithm_version_absent(self, empty_bridge: PAIBridge) -> None:
        """Test functionality: algorithm version absent."""
        assert empty_bridge.get_algorithm_version() is None

    def test_pai_env_empty(self, empty_bridge: PAIBridge) -> None:
        """Test functionality: pai env empty."""
        assert empty_bridge.get_pai_env() == {}
