"""MCP Explorer — demonstrates codomyrmex model_context_protocol, skills, plugin_system.

Integrates with:
- codomyrmex.model_context_protocol for MCP tool discovery, taxonomy, circuit breakers
- codomyrmex.skills for skill registry, loading, and management
- codomyrmex.plugin_system for plugin discovery and dependency resolution
- codomyrmex.logging_monitoring for structured logging

Example:
    >>> explorer = MCPExplorer()
    >>> tools = explorer.list_tools()
    >>> print(tools["discovery_available"])
    >>> skills = explorer.discover_skills()
    >>> print(skills["registry_type"])
"""

from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol import (
    MCPDiscovery,
    MCPToolRegistry,
    ToolCategory,
    categorize_all_tools,
    generate_taxonomy_report,
)
from codomyrmex.plugin_system import (
    Plugin,
    PluginLoader,
    PluginManager,
    PluginRegistry,
    PluginState,
    PluginType,
)
from codomyrmex.skills import (
    SkillLoader,
    SkillRegistry,
    SkillsManager,
    get_skills_manager,
    list_runnable_skills,
)

HAS_MCP_MODULES = True  # Exported for integration tests

logger = get_logger(__name__)


class MCPExplorer:
    """Demonstrates model_context_protocol + skills + plugin_system integration.

    Provides unified discovery of MCP tools, skills, and plugins —
    the three extensibility layers of the codomyrmex platform.

    Attributes:
        discovery: MCPDiscovery instance for tool discovery.
        skill_registry: SkillRegistry for skill management.
        plugin_registry: PluginRegistry for plugin listing.

    Example:
        >>> explorer = MCPExplorer()
        >>> taxonomy = explorer.list_tools()
        >>> print(taxonomy["categories"])
    """

    def __init__(self) -> None:
        """Initialize MCPExplorer."""
        self.discovery = MCPDiscovery()
        self.skill_registry = SkillRegistry()
        self.plugin_registry = PluginRegistry()
        self.plugin_manager = PluginManager()
        logger.info("MCPExplorer initialized")

    def list_tools(self) -> dict[str, Any]:
        """Discover and categorize MCP tools via model_context_protocol.

        Uses MCPDiscovery to scan auto-discovered modules and
        ToolCategory taxonomy to classify them.

        Returns:
            Dictionary with:
            - discovery_available: bool
            - tool_count: int
            - categories: list of ToolCategory values
            - taxonomy_report: dict from generate_taxonomy_report()
        """
        logger.info("Listing MCP tools via MCPDiscovery")

        result: dict[str, Any] = {
            "discovery_available": True,
            "registry_class": MCPToolRegistry.__name__,
            "categories": [cat.value for cat in ToolCategory],
            "tool_count": 0,
            "taxonomy_report": {},
        }

        try:
            report = self.discovery.discover()
            result["tool_count"] = report.total_tools if hasattr(report, "total_tools") else 0
            result["failed_modules"] = report.failed_count if hasattr(report, "failed_count") else 0
        except Exception as e:
            logger.warning(f"MCPDiscovery.discover() failed: {e}")
            result["discovery_error"] = str(e)

        try:
            taxonomy = generate_taxonomy_report()
            result["taxonomy_report"] = (
                taxonomy.__dict__ if hasattr(taxonomy, "__dict__") else str(taxonomy)
            )
        except Exception as e:
            logger.warning(f"generate_taxonomy_report failed: {e}")

        try:
            categorized = categorize_all_tools()
            result["categorized_count"] = len(categorized) if categorized else 0
        except Exception as e:
            logger.warning(f"categorize_all_tools failed: {e}")

        return result

    def discover_skills(self) -> dict[str, Any]:
        """Discover available skills via codomyrmex.skills.

        Uses SkillRegistry and list_runnable_skills to enumerate
        locally available skills.

        Returns:
            Dictionary with:
            - registry_type: str (class name)
            - skill_count: int
            - skills: list of skill names
        """
        logger.info("Discovering skills via SkillRegistry")

        result: dict[str, Any] = {
            "registry_type": SkillRegistry.__name__,
            "loader_type": SkillLoader.__name__,
            "manager_type": SkillsManager.__name__,
            "skill_count": 0,
            "skills": [],
        }

        try:
            skills = self.skill_registry.list_skills()
            result["skill_count"] = len(skills) if skills else 0
            result["skills"] = list(skills)[:20] if skills else []
        except Exception as e:
            logger.warning(f"SkillRegistry.list_skills() failed: {e}")
            result["error"] = str(e)

        try:
            runnable = list_runnable_skills()
            result["runnable_count"] = len(runnable) if runnable else 0
        except Exception as e:
            logger.warning(f"list_runnable_skills() failed: {e}")

        return result

    def scan_plugins(self) -> dict[str, Any]:
        """Scan for installed plugins via plugin_system.

        Uses PluginRegistry to list all known plugins and their
        states (loaded, enabled, disabled, error).

        Returns:
            Dictionary with:
            - registry_type: str
            - plugin_types: list of PluginType values
            - plugin_states: list of PluginState values
            - plugins: list of plugin info dicts
            - plugin_count: int
        """
        logger.info("Scanning plugins via PluginRegistry")

        result: dict[str, Any] = {
            "registry_type": PluginRegistry.__name__,
            "loader_type": PluginLoader.__name__,
            "manager_type": PluginManager.__name__,
            "plugin_class": Plugin.__name__,
            "plugin_types": [pt.value for pt in PluginType],
            "plugin_states": [ps.value for ps in PluginState],
            "plugin_count": 0,
            "plugins": [],
        }

        try:
            plugins = self.plugin_registry.list_plugins()
            result["plugin_count"] = len(plugins) if plugins else 0
            result["plugins"] = [
                {
                    "name": p.name,
                    "version": getattr(p, "version", "unknown"),
                    "state": p.state.value if hasattr(p.state, "value") else str(p.state),
                }
                for p in (plugins or [])
            ]
        except Exception as e:
            logger.warning(f"PluginRegistry.list_plugins() failed: {e}")
            result["error"] = str(e)

        return result

    @staticmethod
    def module_capabilities() -> dict[str, Any]:
        """Return a summary of the MCP/skills/plugin system capabilities.

        Returns:
            Dictionary describing integration affordances.
        """
        return {
            "model_context_protocol": {
                "module": "codomyrmex.model_context_protocol",
                "key_classes": ["MCPDiscovery", "MCPToolRegistry", "MCPServer", "MCPClient"],
                "key_functions": ["categorize_all_tools", "generate_taxonomy_report"],
            },
            "skills": {
                "module": "codomyrmex.skills",
                "key_classes": ["SkillRegistry", "SkillLoader", "SkillsManager"],
                "key_functions": ["list_runnable_skills", "run_skill", "get_skills_manager"],
            },
            "plugin_system": {
                "module": "codomyrmex.plugin_system",
                "key_classes": ["PluginManager", "PluginRegistry", "PluginLoader"],
                "plugin_types": [pt.value for pt in PluginType],
            },
        }
