from typing import Dict, List, Any, Optional, Callable
import inspect
import logging

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.logging_monitoring.logger_config import get_logger







Plugin Registry for Codomyrmex Plugin System

This module defines the core plugin interfaces and registry for managing
plugin discovery, loading, and lifecycle management.
"""

# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

class PluginState(Enum):
    """Plugin lifecycle states."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"

class PluginType(Enum):
    """Plugin type classifications."""
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    INTEGRATION = "integration"
    TRANSFORMATION = "transformation"
    UTILITY = "utility"
    EXTENSION = "extension"

@dataclass
class PluginInfo:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    entry_point: str
    dependencies: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "plugin_type": self.plugin_type.value,
            "entry_point": self.entry_point,
            "dependencies": self.dependencies,
            "config_schema": self.config_schema,
            "homepage": self.homepage,
            "license": self.license,
            "tags": self.tags
        }

class PluginHook:
    """Represents a plugin hook point."""

    def __init__(self, name: str, signature: Optional[Callable] = None, description: str = ""):
        """
        Initialize a plugin hook.

        Args:
            name: Hook name
            signature: Expected function signature
            description: Hook description
        """
        self.name = name
        self.signature = signature
        self.description = description
        self.handlers: List[Callable] = []

    def register(self, handler: Callable) -> None:
        """
        Register a handler for this hook.

        Args:
            handler: Handler function
        """
        if self.signature and not self._check_signature(handler):
            logger.warning(f"Handler {handler} does not match hook {self.name} signature")
            return

        self.handlers.append(handler)
        logger.debug(f"Registered handler for hook '{self.name}'")

    def unregister(self, handler: Callable) -> None:
        """
        Unregister a handler.

        Args:
            handler: Handler function to remove
        """
        if handler in self.handlers:
            self.handlers.remove(handler)
            logger.debug(f"Unregistered handler for hook '{self.name}'")

    def emit(self, *args, **kwargs) -> List[Any]:
        """
        Emit hook to all registered handlers.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            List of results from all handlers
        """
        results = []
        for handler in self.handlers:
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in hook handler for '{self.name}': {e}")

        return results

    def _check_signature(self, handler: Callable) -> bool:
        """Check if handler matches expected signature."""
        try:
            expected_sig = inspect.signature(self.signature)
            handler_sig = inspect.signature(handler)

            # Check parameter compatibility
            expected_params = list(expected_sig.parameters.keys())
            handler_params = list(handler_sig.parameters.keys())

            # Handler must accept at least the expected parameters
            return all(param in handler_params for param in expected_params)

        except Exception:
            return False

class Plugin(ABC):
    """
    Base class for all Codomyrmex plugins.

    Plugins should inherit from this class and implement the required methods.
    """

    def __init__(self, info: PluginInfo):
        """
        Initialize the plugin.

        Args:
            info: Plugin metadata
        """
        self.info = info
        self.state = PluginState.UNLOADED
        self.config: Dict[str, Any] = {}
        self.hooks: Dict[str, PluginHook] = {}

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin.

        Args:
            config: Plugin configuration

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the plugin."""
        pass

    def get_info(self) -> PluginInfo:
        """Get plugin information."""
        return self.info

    def get_state(self) -> PluginState:
        """Get current plugin state."""
        return self.state

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set plugin configuration."""
        self.config = config

    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration."""
        return self.config.copy()

    def register_hook(self, hook_name: str, handler: Callable, description: str = "") -> None:
        """
        Register a hook handler.

        Args:
            hook_name: Name of the hook
            handler: Handler function
            description: Handler description
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = PluginHook(hook_name, description=description)

        self.hooks[hook_name].register(handler)

    def unregister_hook(self, hook_name: str, handler: Callable) -> None:
        """
        Unregister a hook handler.

        Args:
            hook_name: Hook name
            handler: Handler function
        """
        if hook_name in self.hooks:
            self.hooks[hook_name].unregister(handler)

    def emit_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Emit a hook to registered handlers.

        Args:
            hook_name: Name of the hook
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            List of results from handlers
        """
        if hook_name in self.hooks:
            return self.hooks[hook_name].emit(*args, **kwargs)
        return []

class PluginRegistry:
    """
    Registry for managing plugin metadata and discovery.

    Provides centralized storage and retrieval of plugin information,
    dependency management, and plugin compatibility checking.
    """

    def __init__(self):
        """Initialize the plugin registry."""
        self.plugins: Dict[str, PluginInfo] = {}
        self.categories: Dict[str, List[str]] = {}
        self.hooks: Dict[str, PluginHook] = {}

    def register_plugin(self, plugin: Plugin) -> None:
        """
        Register a plugin in the registry.

        Args:
            plugin: Plugin instance to register
        """
        info = plugin.get_info()
        self.plugins[info.name] = info

        # Add to category
        category = info.plugin_type.value
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(info.name)

        logger.info(f"Registered plugin: {info.name} v{info.version}")

    def unregister_plugin(self, plugin_name: str) -> None:
        """
        Unregister a plugin from the registry.

        Args:
            plugin_name: Name of the plugin to unregister
        """
        if plugin_name in self.plugins:
            info = self.plugins[plugin_name]

            # Remove from category
            category = info.plugin_type.value
            if category in self.categories and plugin_name in self.categories[category]:
                self.categories[category].remove(plugin_name)

            del self.plugins[plugin_name]
            logger.info(f"Unregistered plugin: {plugin_name}")

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """
        Get plugin information by name.

        Args:
            plugin_name: Name of the plugin

        Returns:
            PluginInfo if found, None otherwise
        """
        return self.plugins.get(plugin_name)

    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[PluginInfo]:
        """
        List all registered plugins, optionally filtered by type.

        Args:
            plugin_type: Optional plugin type filter

        Returns:
            List of PluginInfo objects
        """
        if plugin_type:
            category_plugins = self.categories.get(plugin_type.value, [])
            return [self.plugins[name] for name in category_plugins if name in self.plugins]
        else:
            return list(self.plugins.values())

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInfo]:
        """
        Get plugins by type.

        Args:
            plugin_type: Type of plugins to retrieve

        Returns:
            List of PluginInfo objects
        """
        return self.list_plugins(plugin_type)

    def get_plugins_by_tag(self, tag: str) -> List[PluginInfo]:
        """
        Get plugins by tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of PluginInfo objects
        """
        return [info for info in self.plugins.values() if tag in info.tags]

    def check_dependencies(self, plugin_name: str) -> List[str]:
        """
        Check if a plugin's dependencies are satisfied.

        Args:
            plugin_name: Name of the plugin to check

        Returns:
            List of missing dependencies
        """
        if plugin_name not in self.plugins:
            return [f"Plugin '{plugin_name}' not registered"]

        info = self.plugins[plugin_name]
        missing = []

        for dep in info.dependencies:
            if dep not in self.plugins:
                missing.append(dep)

        return missing

    def get_dependency_graph(self, plugin_name: str) -> Dict[str, List[str]]:
        """
        Get the dependency graph for a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Dictionary mapping plugin names to their dependencies
        """
        graph = {}
        visited = set()

        def build_graph(name: str) -> None:
    """Brief description of build_graph.

Args:
    name : Description of name

    Returns: Description of return value (type: Any)
"""
            if name in visited:
                return

            visited.add(name)
            if name in self.plugins:
                deps = self.plugins[name].dependencies
                graph[name] = deps
                for dep in deps:
                    build_graph(dep)

        build_graph(plugin_name)
        return graph

    def validate_plugin_compatibility(self, plugin_name: str, target_version: str) -> bool:
        """
        Validate plugin compatibility with a target Codomyrmex version.

        Args:
            plugin_name: Name of the plugin
            target_version: Target Codomyrmex version

        Returns:
            True if compatible
        """
        # Placeholder implementation
        # In a real system, this would check version constraints
        return True

    def search_plugins(self, query: str) -> List[PluginInfo]:
        """
        Search plugins by name, description, or tags.

        Args:
            query: Search query string

        Returns:
            List of matching PluginInfo objects
        """
        query_lower = query.lower()
        matches = []

        for info in self.plugins.values():
            if (query_lower in info.name.lower() or
                query_lower in info.description.lower() or
                any(query_lower in tag.lower() for tag in info.tags)):
                matches.append(info)

        return matches

    def export_registry(self) -> Dict[str, Any]:
        """
        Export the entire registry as a dictionary.

        Returns:
            Registry data as dictionary
        """
        return {
            "plugins": {name: info.to_dict() for name, info in self.plugins.items()},
            "categories": self.categories.copy(),
            "total_plugins": len(self.plugins)
        }

    def import_registry(self, data: Dict[str, Any]) -> None:
        """
        Import registry data from a dictionary.

        Args:
            data: Registry data dictionary
        """
        # Clear existing data
        self.plugins.clear()
        self.categories.clear()

        # Import plugins
        for name, info_dict in data.get("plugins", {}).items():
            # Convert back to PluginInfo
            info_dict_copy = info_dict.copy()
            info_dict_copy["plugin_type"] = PluginType(info_dict["plugin_type"])
            info = PluginInfo(**info_dict_copy)
            self.plugins[name] = info

            # Add to category
            category = info.plugin_type.value
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(name)

        logger.info(f"Imported {len(self.plugins)} plugins into registry")

    # Hook management methods

    def register_global_hook(self, hook_name: str, signature: Optional[Callable] = None, description: str = "") -> PluginHook:
        """
        Register a global hook that plugins can connect to.

        Args:
            hook_name: Name of the hook
            signature: Expected function signature
            description: Hook description

        Returns:
            PluginHook instance
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = PluginHook(hook_name, signature, description)

        return self.hooks[hook_name]

    def get_global_hook(self, hook_name: str) -> Optional[PluginHook]:
        """
        Get a global hook by name.

        Args:
            hook_name: Name of the hook

        Returns:
            PluginHook if found, None otherwise
        """
        return self.hooks.get(hook_name)

    def emit_global_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Emit a global hook to all registered handlers.

        Args:
            hook_name: Name of the hook
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            List of results from all handlers
        """
        if hook_name in self.hooks:
            return self.hooks[hook_name].emit(*args, **kwargs)
        return []

# Convenience functions

def create_plugin_info(**kwargs) -> PluginInfo:
    """
    Convenience function to create PluginInfo.

    Args:
        **kwargs: PluginInfo constructor arguments

    Returns:
        PluginInfo instance
    """
    return PluginInfo(**kwargs)

def get_registry() -> PluginRegistry:
    """
    Get the global plugin registry instance.

    Returns:
        PluginRegistry instance
    """
    if not hasattr(get_registry, '_registry'):
        get_registry._registry = PluginRegistry()
    return get_registry._registry
