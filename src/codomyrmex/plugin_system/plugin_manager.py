"""
Plugin Manager for Codomyrmex Plugin System

This module provides the main plugin management interface, coordinating
plugin discovery, validation, loading, and lifecycle management.
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

# Import logging
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Import plugin system components
from .plugin_registry import PluginRegistry, Plugin, PluginInfo, PluginType
from .plugin_validator import PluginValidator, ValidationResult
from .plugin_loader import PluginLoader, LoadResult


class PluginManager:
    """
    Central plugin management system for Codomyrmex.

    Coordinates plugin discovery, validation, loading, and provides
    a unified interface for plugin lifecycle management.
    """

    def __init__(self, plugin_directories: Optional[List[str]] = None):
        """
        Initialize the plugin manager.

        Args:
            plugin_directories: List of directories to search for plugins
        """
        self.registry = PluginRegistry()
        self.validator = PluginValidator()
        self.loader = PluginLoader(plugin_directories)

        # Plugin management state
        self.auto_discover = True
        self.auto_validate = True
        self.parallel_loading = True

        logger.info("PluginManager initialized")

    def discover_plugins(self) -> List[PluginInfo]:
        """
        Discover available plugins.

        Returns:
            List of discovered PluginInfo objects
        """
        logger.info("Discovering plugins...")
        plugins = self.loader.discover_plugins()

        # Register discovered plugins
        for plugin_info in plugins:
            self.registry.register_plugin(Plugin())  # Placeholder plugin instance
            logger.debug(f"Discovered plugin: {plugin_info.name}")

        return plugins

    def validate_plugin(self, plugin_path: str) -> ValidationResult:
        """
        Validate a plugin for security and compatibility.

        Args:
            plugin_path: Path to the plugin

        Returns:
            ValidationResult with detailed findings
        """
        logger.info(f"Validating plugin: {plugin_path}")
        return self.validator.validate_plugin(plugin_path)

    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> LoadResult:
        """
        Load and initialize a plugin.

        Args:
            plugin_name: Name of the plugin to load
            config: Plugin configuration

        Returns:
            LoadResult with loading outcome
        """
        logger.info(f"Loading plugin: {plugin_name}")

        # Get plugin info from registry
        plugin_info = self.registry.get_plugin_info(plugin_name)
        if not plugin_info:
            return LoadResult(
                plugin_name=plugin_name,
                success=False,
                error_message="Plugin not found in registry"
            )

        # Validate if auto-validation is enabled
        if self.auto_validate:
            validation_result = self.validate_plugin(plugin_info.entry_point)
            if not validation_result.is_valid:
                return LoadResult(
                    plugin_name=plugin_name,
                    success=False,
                    error_message=f"Plugin validation failed: {len(validation_result.issues)} issues",
                    warnings=[issue['message'] for issue in validation_result.issues + validation_result.warnings]
                )

        # Load the plugin
        result = self.loader.load_plugin(plugin_info, config)

        if result.success and result.plugin_instance:
            # Register the loaded plugin in the registry
            self.registry.register_plugin(result.plugin_instance)

        return result

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            True if successfully unloaded
        """
        logger.info(f"Unloading plugin: {plugin_name}")

        success = self.loader.unload_plugin(plugin_name)
        if success:
            # Remove from registry
            self.registry.unregister_plugin(plugin_name)

        return success

    def reload_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> LoadResult:
        """
        Reload a plugin.

        Args:
            plugin_name: Name of the plugin
            config: New plugin configuration

        Returns:
            LoadResult with reload outcome
        """
        logger.info(f"Reloading plugin: {plugin_name}")

        return self.loader.reload_plugin(plugin_name, config)

    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a loaded plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            True if successfully enabled
        """
        plugin = self.loader.get_plugin(plugin_name)
        if plugin:
            plugin.state = PluginState.ACTIVE
            logger.info(f"Enabled plugin: {plugin_name}")
            return True

        logger.warning(f"Plugin not found for enabling: {plugin_name}")
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a loaded plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            True if successfully disabled
        """
        plugin = self.loader.get_plugin(plugin_name)
        if plugin:
            plugin.state = PluginState.DISABLED
            logger.info(f"Disabled plugin: {plugin_name}")
            return True

        logger.warning(f"Plugin not found for disabling: {plugin_name}")
        return False

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a loaded plugin instance.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin instance if loaded, None otherwise
        """
        return self.loader.get_plugin(plugin_name)

    def list_plugins(self, filter_type: Optional[PluginType] = None, include_loaded: bool = True) -> List[PluginInfo]:
        """
        List available plugins.

        Args:
            filter_type: Optional plugin type filter
            include_loaded: Whether to include loaded status

        Returns:
            List of PluginInfo objects
        """
        plugins = self.registry.list_plugins(filter_type)

        if include_loaded:
            # Add loaded status
            loaded_plugins = self.loader.get_loaded_plugins()
            for plugin_info in plugins:
                plugin_info.tags = plugin_info.tags or []
                if plugin_info.name in loaded_plugins:
                    if "loaded" not in plugin_info.tags:
                        plugin_info.tags.append("loaded")
                else:
                    if "loaded" in plugin_info.tags:
                        plugin_info.tags.remove("loaded")

        return plugins

    async def load_plugins_async(self, plugin_names: List[str], configs: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, LoadResult]:
        """
        Load multiple plugins asynchronously.

        Args:
            plugin_names: List of plugin names to load
            configs: Optional configurations for each plugin

        Returns:
            Dictionary mapping plugin names to LoadResult objects
        """
        configs = configs or {}

        async def load_single_plugin(name: str) -> LoadResult:
            config = configs.get(name)
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor, self.load_plugin, name, config
                )
                return result

        # Load plugins concurrently
        tasks = [load_single_plugin(name) for name in plugin_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        result_dict = {}
        for name, result in zip(plugin_names, results):
            if isinstance(result, Exception):
                result_dict[name] = LoadResult(
                    plugin_name=name,
                    success=False,
                    error_message=str(result)
                )
            else:
                result_dict[name] = result

        return result_dict

    def get_plugin_status(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get status of a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Dictionary with plugin status information
        """
        status = {
            "name": plugin_name,
            "registered": False,
            "loaded": False,
            "state": "unknown",
            "validation_score": None,
            "dependencies_satisfied": None
        }

        # Check registry
        plugin_info = self.registry.get_plugin_info(plugin_name)
        if plugin_info:
            status["registered"] = True
            status["info"] = plugin_info.to_dict()

            # Check dependencies
            missing_deps = self.registry.check_dependencies(plugin_name)
            status["dependencies_satisfied"] = len(missing_deps) == 0
            status["missing_dependencies"] = missing_deps

        # Check loader
        plugin_instance = self.loader.get_plugin(plugin_name)
        if plugin_instance:
            status["loaded"] = True
            status["state"] = plugin_instance.get_state().value

        return status

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall plugin system status.

        Returns:
            Dictionary with system-wide plugin status
        """
        all_plugins = self.registry.list_plugins()
        loaded_plugins = self.loader.get_loaded_plugins()

        status_counts = {
            "total_registered": len(all_plugins),
            "total_loaded": len(loaded_plugins),
            "by_type": {},
            "by_state": {}
        }

        # Count by type
        for plugin_info in all_plugins:
            plugin_type = plugin_info.plugin_type.value
            status_counts["by_type"][plugin_type] = status_counts["by_type"].get(plugin_type, 0) + 1

        # Count by state
        for plugin in loaded_plugins.values():
            state = plugin.get_state().value
            status_counts["by_state"][state] = status_counts["by_state"].get(state, 0) + 1

        # Check for issues
        issues = []
        for plugin_info in all_plugins:
            missing_deps = self.registry.check_dependencies(plugin_info.name)
            if missing_deps:
                issues.append(f"{plugin_info.name}: missing dependencies {missing_deps}")

        return {
            "status_counts": status_counts,
            "issues": issues,
            "system_health": "healthy" if not issues else "degraded"
        }

    def register_hook(self, hook_name: str, signature: Optional[Callable] = None, description: str = "") -> None:
        """
        Register a global hook that plugins can connect to.

        Args:
            hook_name: Name of the hook
            signature: Expected function signature
            description: Hook description
        """
        self.registry.register_global_hook(hook_name, signature, description)
        logger.info(f"Registered global hook: {hook_name}")

    def emit_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Emit a global hook to all registered handlers.

        Args:
            hook_name: Name of the hook
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            List of results from all handlers
        """
        return self.registry.emit_global_hook(hook_name, *args, **kwargs)

    def save_plugin_registry(self, file_path: str) -> None:
        """
        Save the plugin registry to a file.

        Args:
            file_path: Path to save the registry
        """
        import json
        registry_data = self.registry.export_registry()

        with open(file_path, 'w') as f:
            json.dump(registry_data, f, indent=2)

        logger.info(f"Plugin registry saved to {file_path}")

    def load_plugin_registry(self, file_path: str) -> None:
        """
        Load the plugin registry from a file.

        Args:
            file_path: Path to load the registry from
        """
        import json

        with open(file_path, 'r') as f:
            registry_data = json.load(f)

        self.registry.import_registry(registry_data)
        logger.info(f"Plugin registry loaded from {file_path}")

    def cleanup(self) -> None:
        """
        Clean up the plugin manager and unload all plugins.
        """
        logger.info("Cleaning up plugin manager...")

        loaded_plugins = list(self.loader.get_loaded_plugins().keys())
        for plugin_name in loaded_plugins:
            self.unload_plugin(plugin_name)

        logger.info("Plugin manager cleanup complete")


# Convenience functions

def get_plugin_manager() -> PluginManager:
    """
    Get the global plugin manager instance.

    Returns:
        PluginManager instance
    """
    if not hasattr(get_plugin_manager, '_manager'):
        get_plugin_manager._manager = PluginManager()
    return get_plugin_manager._manager


def discover_plugins() -> List[PluginInfo]:
    """
    Convenience function to discover plugins.

    Returns:
        List of discovered PluginInfo objects
    """
    manager = get_plugin_manager()
    return manager.discover_plugins()


def load_plugin(plugin_name: str, config: Optional[Dict[str, Any]] = None) -> LoadResult:
    """
    Convenience function to load a plugin.

    Args:
        plugin_name: Name of the plugin
        config: Plugin configuration

    Returns:
        LoadResult with loading outcome
    """
    manager = get_plugin_manager()
    return manager.load_plugin(plugin_name, config)


def unload_plugin(plugin_name: str) -> bool:
    """
    Convenience function to unload a plugin.

    Args:
        plugin_name: Name of the plugin

    Returns:
        True if successfully unloaded
    """
    manager = get_plugin_manager()
    return manager.unload_plugin(plugin_name)
