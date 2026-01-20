"""Plugin Registry for Codomyrmex Plugin System.

Defines the core plugin interfaces and registry for managing plugins.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

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
    UTILITY = "utility"
    ADAPTER = "adapter"
    AGENT = "agent"


class PluginState(Enum):
    """Lifecycle state of a plugin."""
    UNKNOWN = "unknown"
    REGISTERED = "registered"
    LOADED = "loaded"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"
    INITIALIZING = "initializing"
    SHUTTING_DOWN = "shutting_down"
    LOADING = "loading"
    UNLOADED = "unloaded"


@dataclass
class PluginInfo:
    """Plugin metadata."""
    name: str = ""
    version: str = "0.0.0"
    description: str = ""
    author: Optional[str] = None
    plugin_type: PluginType = PluginType.UTILITY
    entry_point: str = ""
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    homepage: Optional[str] = None
    license: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert PluginInfo to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "plugin_type": self.plugin_type.value if hasattr(self.plugin_type, 'value') else str(self.plugin_type),
            "entry_point": self.entry_point,
            "dependencies": self.dependencies,
            "enabled": self.enabled,
            "tags": self.tags,
            "config_schema": self.config_schema,
            "homepage": self.homepage,
            "license": self.license
        }


class Hook:
    """Represents a plugin hook."""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.handlers: List[Callable] = []

    def register(self, handler: Callable):
        self.handlers.append(handler)

    def emit(self, *args, **kwargs) -> List[Any]:
        results = []
        for handler in self.handlers:
            try:
                results.append(handler(*args, **kwargs))
            except Exception as e:
                logger.error(f"Error in hook {self.name}: {e}")
        return results


class Plugin:
    """Base class for all plugins."""

    def __init__(self, info: Union[PluginInfo, Any] = None):
        """Initialize plugin with metadata."""
        if isinstance(info, PluginInfo):
            self._info = info
        elif info is not None:
             self._info = PluginInfo(name=getattr(info, 'name', 'unnamed'), 
                                     version=getattr(info, 'version', '0.0.0'),
                                     description=getattr(info, 'description', ''))
        else:
             self._info = PluginInfo()
             
        self.state = PluginState.UNLOADED
        self.config: Dict[str, Any] = {}
        self.hooks: Dict[str, Hook] = {}

    @property
    def info(self) -> PluginInfo:
        """Get plugin info."""
        return self._info

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the plugin."""
        if config:
            self.config.update(config)
        self.state = PluginState.ACTIVE
        return True

    def shutdown(self) -> bool:
        """Shutdown the plugin."""
        self.state = PluginState.SHUTTING_DOWN
        return True

    def register_hook(self, name: str, handler: Callable):
        """Register a hook for this plugin."""
        if name not in self.hooks:
            self.hooks[name] = Hook(name)
        self.hooks[name].register(handler)

    def emit_hook(self, name: str, *args, **kwargs) -> List[Any]:
        """Emit a hook for this plugin."""
        if name in self.hooks:
            return self.hooks[name].emit(*args, **kwargs)
        return []

    def get_state(self) -> PluginState:
        """Return current plugin state."""
        return self.state

    def set_config(self, config: Dict[str, Any]):
        """Set plugin configuration."""
        self.config = config

    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration."""
        return self.config


class PluginRegistry:
    """Registry for managing plugins."""

    def __init__(self):
        """Initialize registry."""
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_info: Dict[str, PluginInfo] = {}
        self._global_hooks: Dict[str, Hook] = {}
        self.categories: Dict[str, List[str]] = {}
        self.capabilities: Dict[str, List[str]] = {}


    def register_global_hook(self, name: str, signature: Optional[Callable] = None, description: str = "") -> Hook:
        """Register a global entry point for hooks."""
        if name not in self._global_hooks:
            self._global_hooks[name] = Hook(name, description)
        return self._global_hooks[name]

    def emit_global_hook(self, name: str, *args, **kwargs) -> List[Any]:
        """Emit a global hook."""
        if name in self._global_hooks:
            return self._global_hooks[name].emit(*args, **kwargs)
        return []


    def register(self, plugin: Plugin) -> bool:
        """Register a plugin."""
        info = plugin.info
        if info.name in self._plugins:
            logger.warning(f"Plugin {info.name} already registered")
            return False

        self._plugins[info.name] = plugin
        self._plugin_info[info.name] = info
        
        # Update categories
        cat_key = info.plugin_type.value if hasattr(info.plugin_type, 'value') else str(info.plugin_type)
        if cat_key not in self.categories:
            self.categories[cat_key] = []
        if info.name not in self.categories[cat_key]:
            self.categories[cat_key].append(info.name)

        logger.info(f"Registered plugin: {info.name} v{info.version}")
        return True

    def unregister(self, name: str) -> bool:
        """Unregister a plugin."""
        if name not in self._plugins:
            return False

        plugin = self._plugins[name]
        plugin.shutdown()
        
        info = self._plugin_info[name]
        cat_key = info.plugin_type.value if hasattr(info.plugin_type, 'value') else str(info.plugin_type)
        if cat_key in self.categories and name in self.categories[cat_key]:
            self.categories[cat_key].remove(name)

        del self._plugins[name]
        del self._plugin_info[name]
        logger.info(f"Unregistered plugin: {name}")
        return True

    def get(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def get_plugin_info(self, name: str) -> Optional[PluginInfo]:
        """Get plugin metadata by name."""
        return self._plugin_info.get(name)

    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[PluginInfo]:
        """List all plugins, optionally filtered by type."""
        plugins = list(self._plugin_info.values())
        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]
        return plugins

    def check_dependencies(self, name: str) -> List[str]:
        """Check if plugin dependencies are satisfied."""
        if name not in self._plugin_info:
            return []
        
        info = self._plugin_info[name]
        missing = []
        for dep in info.dependencies:
            if dep not in self._plugins:
                missing.append(dep)
        return missing

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

def create_plugin_info(**kwargs) -> PluginInfo:
    """Helper to create PluginInfo."""
    return PluginInfo(**kwargs)
