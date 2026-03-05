"""Integration tests for mcp_explorer.py — model_context_protocol + skills + plugin_system."""

import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMCPProtocolImports:
    """Verify codomyrmex.model_context_protocol imports used in mcp_explorer."""

    def test_import_mcp_discovery(self):
        """MCPDiscovery is importable and constructable."""
        from codomyrmex.model_context_protocol import MCPDiscovery

        discovery = MCPDiscovery()
        assert discovery is not None

    def test_import_mcp_tool_registry(self):
        """MCPToolRegistry is importable."""
        from codomyrmex.model_context_protocol import MCPToolRegistry

        assert MCPToolRegistry is not None

    def test_import_tool_category(self):
        """ToolCategory enum is importable and has values."""
        from codomyrmex.model_context_protocol import ToolCategory

        assert ToolCategory is not None
        values = [cat.value for cat in ToolCategory]
        assert len(values) > 0

    def test_import_categorize_all_tools(self):
        """categorize_all_tools is importable and callable."""
        from codomyrmex.model_context_protocol import categorize_all_tools

        assert callable(categorize_all_tools)

    def test_import_generate_taxonomy_report(self):
        """generate_taxonomy_report is importable and callable."""
        from codomyrmex.model_context_protocol import generate_taxonomy_report

        assert callable(generate_taxonomy_report)

    def test_import_circuit_breaker(self):
        """CircuitBreaker is importable."""
        from codomyrmex.model_context_protocol import CircuitBreaker, CircuitState

        assert CircuitBreaker is not None
        assert CircuitState is not None


class TestSkillsImports:
    """Verify codomyrmex.skills imports used in mcp_explorer."""

    def test_import_skill_registry(self):
        """SkillRegistry is importable and constructable with a SkillLoader."""
        from pathlib import Path

        from codomyrmex.skills import SkillLoader, SkillRegistry

        skills_dir = Path.home() / ".claude" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        loader = SkillLoader(upstream_dir=skills_dir, custom_dir=skills_dir)
        registry = SkillRegistry(skill_loader=loader)
        assert registry is not None

    def test_import_skill_loader(self):
        """SkillLoader is importable."""
        from codomyrmex.skills import SkillLoader

        assert SkillLoader is not None

    def test_import_skills_manager(self):
        """SkillsManager is importable."""
        from codomyrmex.skills import SkillsManager

        assert SkillsManager is not None

    def test_import_list_runnable_skills(self):
        """list_runnable_skills is importable and callable."""
        from codomyrmex.skills import list_runnable_skills

        assert callable(list_runnable_skills)

    def test_import_get_skills_manager(self):
        """get_skills_manager is importable and returns SkillsManager."""
        from codomyrmex.skills import SkillsManager, get_skills_manager

        manager = get_skills_manager()
        assert isinstance(manager, SkillsManager)


class TestPluginSystemImports:
    """Verify codomyrmex.plugin_system imports used in mcp_explorer."""

    def test_import_plugin_manager(self):
        """PluginManager is importable and constructable."""
        from codomyrmex.plugin_system import PluginManager

        manager = PluginManager()
        assert manager is not None

    def test_import_plugin_registry(self):
        """PluginRegistry is importable and constructable."""
        from codomyrmex.plugin_system import PluginRegistry

        registry = PluginRegistry()
        assert registry is not None

    def test_import_plugin_type(self):
        """PluginType enum is importable and has values."""
        from codomyrmex.plugin_system import PluginType

        values = [pt.value for pt in PluginType]
        assert len(values) > 0

    def test_import_plugin_state(self):
        """PluginState enum is importable and has values."""
        from codomyrmex.plugin_system import PluginState

        values = [ps.value for ps in PluginState]
        assert len(values) > 0

    def test_import_plugin_exceptions(self):
        """PluginError and subclasses are importable."""
        from codomyrmex.plugin_system import (
            DependencyError,
            LoadError,
            PluginError,
        )

        assert issubclass(LoadError, PluginError)
        assert issubclass(DependencyError, PluginError)


class TestMCPExplorerModule:
    """Functional tests for MCPExplorer class."""

    def test_has_mcp_modules_flag(self):
        """HAS_MCP_MODULES flag is True in mcp_explorer.py."""
        from src.mcp_explorer import HAS_MCP_MODULES

        assert HAS_MCP_MODULES is True

    def test_mcp_explorer_instantiation(self):
        """MCPExplorer can be instantiated without errors."""
        from src.mcp_explorer import MCPExplorer

        explorer = MCPExplorer()
        assert explorer is not None
        assert explorer.discovery is not None
        assert explorer.skill_registry is not None
        assert explorer.plugin_registry is not None

    def test_list_tools_returns_dict(self):
        """list_tools() returns a dict with expected keys."""
        from src.mcp_explorer import MCPExplorer

        explorer = MCPExplorer()
        result = explorer.list_tools()
        assert isinstance(result, dict)
        assert "discovery_available" in result
        assert "categories" in result
        assert result["discovery_available"] is True
        assert isinstance(result["categories"], list)
        assert len(result["categories"]) > 0

    def test_discover_skills_returns_dict(self):
        """discover_skills() returns a dict with expected keys."""
        from src.mcp_explorer import MCPExplorer

        explorer = MCPExplorer()
        result = explorer.discover_skills()
        assert isinstance(result, dict)
        assert "registry_type" in result
        assert "skill_count" in result
        assert isinstance(result["skill_count"], int)

    def test_scan_plugins_returns_dict(self):
        """scan_plugins() returns a dict with expected keys."""
        from src.mcp_explorer import MCPExplorer

        explorer = MCPExplorer()
        result = explorer.scan_plugins()
        assert isinstance(result, dict)
        assert "plugin_types" in result
        assert "plugin_states" in result
        assert "plugin_count" in result
        assert isinstance(result["plugin_types"], list)

    def test_module_capabilities_returns_expected_keys(self):
        """module_capabilities() returns dict with all three module sections."""
        from src.mcp_explorer import MCPExplorer

        caps = MCPExplorer.module_capabilities()
        assert isinstance(caps, dict)
        assert "model_context_protocol" in caps
        assert "skills" in caps
        assert "plugin_system" in caps
        assert "key_classes" in caps["model_context_protocol"]
