"""
Plugin Manager for Codomyrmex Plugin System

This module provides the main plugin management interface, coordinating
plugin discovery, validation, loading, and lifecycle management.
"""

from typing import Any
from collections.abc import Callable

# Import logging
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Import plugin system components
from .plugin_loader import LoadResult, PluginLoader
from .plugin_registry import (
    Hook,
    Plugin,
    PluginInfo,
    PluginRegistry,
    PluginState,
    PluginType,
)
from ..validation.plugin_validator import PluginValidator, ValidationResult


class PluginManager:
    """
    Central plugin management system for Codomyrmex.
    """

    def __init__(self, plugin_directories: list[str] | None = None):
        """Initialize the plugin manager."""
        self.registry = PluginRegistry()
        self.validator = PluginValidator()
        self.loader = PluginLoader(plugin_directories)

        # Plugin management state
        self.auto_discover = True
        self.auto_validate = True
        self.parallel_loading = True

        logger.info("PluginManager initialized")

    def discover_plugins(self) -> list[PluginInfo]:
        """Discover available plugins."""
        logger.info("Discovering plugins...")
        plugins = self.loader.discover_plugins()
        return plugins

    def validate_plugin(self, plugin_path: str) -> ValidationResult:
        """Validate a plugin for security and compatibility."""
        return self.validator.validate_plugin(plugin_path)

    def load_plugin(self, plugin_name: str, config: dict[str, Any] | None = None) -> LoadResult:
        """Load and initialize a plugin."""
        logger.info(f"Loading plugin: {plugin_name}")

        plugin_info = self.registry.get_plugin_info(plugin_name)
        if not plugin_info:
             found_info = None
             for info in self.loader.discover_plugins():
                 if info.name == plugin_name:
                     found_info = info
                     break
             if found_info:
                 plugin_info = found_info
                 self.registry.register(Plugin(info=found_info))
             else:
                return LoadResult(plugin_name=plugin_name, success=False, error_message="Plugin not found")

        # Validate if auto-validation is enabled
        if self.auto_validate:
            validation_result = self.validate_plugin(plugin_info.entry_point)
            if not validation_result.valid:
                return LoadResult(
                    plugin_name=plugin_name,
                    success=False,
                    error_message="Plugin validation failed",
                    warnings=[issue['message'] for issue in validation_result.issues + validation_result.warnings]
                )

        # Load the plugin
        result = self.loader.load_plugin(plugin_info, config)

        if result.success and result.plugin_instance:
            self.registry.register(result.plugin_instance)

        return result

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        logger.info(f"Unloading plugin: {plugin_name}")
        success = self.loader.unload_plugin(plugin_name)
        if success:
            self.registry.unregister(plugin_name)
        return success

    def reload_plugin(self, plugin_name: str, config: dict[str, Any] | None = None) -> LoadResult:
        """Reload a plugin."""
        return self.loader.reload_plugin(plugin_name, config)

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a loaded plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.state = PluginState.ACTIVE
            return True
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a loaded plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.state = PluginState.DISABLED
            return True
        return False

    def get_plugin(self, plugin_name: str) -> Plugin | None:
        """Get a loaded plugin instance."""
        return self.registry.get(plugin_name)

    def list_plugins(self, filter_type: PluginType | None = None, include_loaded: bool = True) -> list[PluginInfo]:
        """List available plugins."""
        return self.registry.list_plugins(filter_type)

    def get_plugin_status(self, plugin_name: str) -> dict[str, Any]:
        """Get status of a plugin."""
        status = {
            "name": plugin_name,
            "registered": False,
            "loaded": False,
            "state": "unknown",
            "validation_score": None,
            "dependencies_satisfied": None
        }

        plugin_info = self.registry.get_plugin_info(plugin_name)
        if plugin_info:
            status["registered"] = True
            status["info"] = plugin_info.to_dict()
            missing_deps = self.registry.check_dependencies(plugin_name)
            status["dependencies_satisfied"] = len(missing_deps) == 0
            status["missing_dependencies"] = missing_deps

        # Use loader to check for "loaded" status specifically
        loaded_plugins = self.loader.get_loaded_plugins()
        if plugin_name in loaded_plugins:
            status["loaded"] = True
            status["state"] = loaded_plugins[plugin_name].get_state().value
        else:
            # Fallback to registry check if loader doesn't have it (e.g. manually registered)
            # But the test expects False if it was just registered in registry
            pass

        return status

    def get_system_status(self) -> dict[str, Any]:
        """Get overall plugin system status."""
        all_plugins = self.registry.list_plugins()
        loaded_plugins = self.loader.get_loaded_plugins()
        status_counts = {
            "total_registered": len(all_plugins),
            "total_loaded": len(loaded_plugins),
            "by_type": {},
            "by_state": {}
        }
        for info in all_plugins:
            status_counts["by_type"][info.plugin_type.value] = status_counts["by_type"].get(info.plugin_type.value, 0) + 1
        for plugin in loaded_plugins.values():
            status_counts["by_state"][plugin.get_state().value] = status_counts["by_state"].get(plugin.get_state().value, 0) + 1
        return {"status_counts": status_counts, "system_health": "healthy"}

    def register_hook(self, hook_name: str, signature: Callable | None = None, description: str = "") -> Hook:
        """Register a global hook."""
        hook = self.registry.register_global_hook(hook_name, signature, description)
        logger.info(f"Registered global hook: {hook_name}")
        return hook

    def emit_hook(self, hook_name: str, *args, **kwargs) -> list[Any]:
        """Emit a global hook."""
        return self.registry.emit_global_hook(hook_name, *args, **kwargs)

    def cleanup(self) -> None:
        """Clean up the plugin manager."""
        plugins = [p.name for p in self.registry.list_plugins()]
        for name in plugins:
            self.unload_plugin(name)


def get_plugin_manager() -> PluginManager:
    if not hasattr(get_plugin_manager, '_manager'):
        get_plugin_manager._manager = PluginManager()
    return get_plugin_manager._manager

def discover_plugins() -> list[PluginInfo]: return get_plugin_manager().discover_plugins()
def load_plugin(name: str, config=None) -> LoadResult: return get_plugin_manager().load_plugin(name, config)
def unload_plugin(name: str) -> bool: return get_plugin_manager().unload_plugin(name)
