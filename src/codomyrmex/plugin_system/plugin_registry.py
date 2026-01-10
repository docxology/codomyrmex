"""Plugin Registry for Codomyrmex Plugin System.

Defines the core plugin interfaces and registry for managing plugins.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


class PluginType(Enum):
    """Types of plugins."""
    ANALYZER = "analyzer"
    FORMATTER = "formatter"
    EXPORTER = "exporter"
    IMPORTER = "importer"
    PROCESSOR = "processor"
    HOOK = "hook"


@dataclass
class PluginInfo:
    """Plugin metadata."""
    name: str
    version: str
    description: str
    plugin_type: PluginType
    author: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True


class Plugin(ABC):
    """Base class for all plugins."""

    @property
    @abstractmethod
    def info(self) -> PluginInfo:
        """Get plugin info."""
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin."""
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """Shutdown the plugin."""
        pass


class PluginRegistry:
    """Registry for managing plugins."""

    def __init__(self):
        """Initialize registry."""
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_info: Dict[str, PluginInfo] = {}

    def register(self, plugin: Plugin) -> bool:
        """Register a plugin."""
        info = plugin.info
        if info.name in self._plugins:
            logger.warning(f"Plugin {info.name} already registered")
            return False

        self._plugins[info.name] = plugin
        self._plugin_info[info.name] = info
        logger.info(f"Registered plugin: {info.name} v{info.version}")
        return True

    def unregister(self, name: str) -> bool:
        """Unregister a plugin."""
        if name not in self._plugins:
            return False

        plugin = self._plugins[name]
        plugin.shutdown()
        del self._plugins[name]
        del self._plugin_info[name]
        logger.info(f"Unregistered plugin: {name}")
        return True

    def get(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[PluginInfo]:
        """List all plugins, optionally filtered by type."""
        plugins = list(self._plugin_info.values())
        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]
        return plugins

    def initialize_all(self) -> Dict[str, bool]:
        """Initialize all plugins."""
        results = {}
        for name, plugin in self._plugins.items():
            try:
                results[name] = plugin.initialize()
            except Exception as e:
                logger.error(f"Failed to initialize {name}: {e}")
                results[name] = False
        return results

    def shutdown_all(self) -> Dict[str, bool]:
        """Shutdown all plugins."""
        results = {}
        for name, plugin in self._plugins.items():
            try:
                results[name] = plugin.shutdown()
            except Exception as e:
                logger.error(f"Failed to shutdown {name}: {e}")
                results[name] = False
        return results


# Global registry instance
_registry: Optional[PluginRegistry] = None

def get_registry() -> PluginRegistry:
    """Get the global plugin registry."""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry
