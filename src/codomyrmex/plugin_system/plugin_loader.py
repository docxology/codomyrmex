"""
Plugin Loader for Codomyrmex Plugin System

This module handles the loading, initialization, and lifecycle management
of plugins in the Codomyrmex system.
"""

import importlib.util
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass

# Import logging
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Import plugin system components
from .plugin_registry import Plugin, PluginInfo, PluginState


@dataclass
class LoadResult:
    """Result of plugin loading operation."""
    plugin_name: str
    success: bool
    plugin_instance: Optional[Plugin] = None
    error_message: Optional[str] = None
    warnings: List[str] = None

    def __post_init__(self):

        if self.warnings is None:
            self.warnings = []


class PluginLoader:
    """
    Plugin loader responsible for discovering, loading, and initializing plugins.

    Handles dynamic loading of plugin modules, dependency resolution,
    and proper initialization with configuration.
    """

    def __init__(self, plugin_directories: Optional[List[str]] = None):
        """
        Initialize the plugin loader.

        Args:
            plugin_directories: List of directories to search for plugins
        """
        self.plugin_directories = plugin_directories or [
            Path.cwd() / "plugins",
            Path.home() / ".codomyrmex" / "plugins"
        ]

        # Ensure directories exist
        for directory in self.plugin_directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

        self.loaded_plugins: Dict[str, Plugin] = {}
        self.load_cache: Dict[str, Any] = {}

    def discover_plugins(self) -> List[PluginInfo]:
        """
        Discover available plugins in configured directories.

        Returns:
            List of discovered PluginInfo objects
        """
        discovered_plugins = []

        for directory in self.plugin_directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                continue

            # Look for plugin directories and files
            for item in dir_path.iterdir():
                if item.is_dir():
                    # Check if it's a plugin directory
                    plugin_info = self._load_plugin_metadata(item)
                    if plugin_info:
                        discovered_plugins.append(plugin_info)
                elif item.suffix == '.py' and item.name != '__init__.py':
                    # Check if it's a plugin file
                    plugin_info = self._load_plugin_metadata_from_file(item)
                    if plugin_info:
                        discovered_plugins.append(plugin_info)

        logger.info(f"Discovered {len(discovered_plugins)} plugins")
        return discovered_plugins

    def load_plugin(self, plugin_info: PluginInfo, config: Optional[Dict[str, Any]] = None) -> LoadResult:
        """
        Load and initialize a plugin.

        Args:
            plugin_info: Plugin metadata
            config: Plugin configuration

        Returns:
            LoadResult with loading outcome
        """
        result = LoadResult(plugin_name=plugin_info.name, success=False)

        try:
            # Check if already loaded
            if plugin_info.name in self.loaded_plugins:
                result.success = True
                result.plugin_instance = self.loaded_plugins[plugin_info.name]
                result.warnings.append(f"Plugin '{plugin_info.name}' already loaded")
                return result

            # Load the plugin module
            plugin_module = self._load_plugin_module(plugin_info)
            if not plugin_module:
                result.error_message = "Failed to load plugin module"
                return result

            # Find the plugin class
            plugin_class = self._find_plugin_class(plugin_module, plugin_info)
            if not plugin_class:
                result.error_message = "Plugin class not found in module"
                return result

            # Instantiate the plugin
            plugin_instance = plugin_class(plugin_info)
            plugin_instance.state = PluginState.LOADING

            # Initialize with configuration
            plugin_instance.state = PluginState.INITIALIZING
            config = config or {}

            if plugin_instance.initialize(config):
                plugin_instance.state = PluginState.ACTIVE
                self.loaded_plugins[plugin_info.name] = plugin_instance
                result.success = True
                result.plugin_instance = plugin_instance

                logger.info(f"Successfully loaded plugin: {plugin_info.name}")
            else:
                plugin_instance.state = PluginState.ERROR
                result.error_message = "Plugin initialization failed"

        except Exception as e:
            logger.error(f"Error loading plugin '{plugin_info.name}': {e}")
            result.error_message = str(e)

        return result

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if successfully unloaded
        """
        if plugin_name not in self.loaded_plugins:
            logger.warning(f"Plugin '{plugin_name}' not loaded")
            return False

        plugin = self.loaded_plugins[plugin_name]

        try:
            plugin.state = PluginState.UNLOADED
            plugin.shutdown()

            del self.loaded_plugins[plugin_name]

            # Remove from load cache
            if plugin_name in self.load_cache:
                del self.load_cache[plugin_name]

            logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Error unloading plugin '{plugin_name}': {e}")
            plugin.state = PluginState.ERROR
            return False

    def reload_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> LoadResult:
        """
        Reload a plugin.

        Args:
            plugin_name: Name of the plugin to reload
            config: New configuration for the plugin

        Returns:
            LoadResult with reload outcome
        """
        # Unload first
        self.unload_plugin(plugin_name)

        # Find plugin info (this would normally come from registry)
        # For now, we'll need to rediscover
        discovered = self.discover_plugins()
        plugin_info = next((p for p in discovered if p.name == plugin_name), None)

        if not plugin_info:
            return LoadResult(
                plugin_name=plugin_name,
                success=False,
                error_message="Plugin not found during rediscovery"
            )

        # Load again
        return self.load_plugin(plugin_info, config)

    def get_loaded_plugins(self) -> Dict[str, Plugin]:
        """
        Get all currently loaded plugins.

        Returns:
            Dictionary of plugin name to Plugin instance
        """
        return self.loaded_plugins.copy()

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a loaded plugin by name.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin instance if loaded, None otherwise
        """
        return self.loaded_plugins.get(plugin_name)

    def validate_plugin_dependencies(self, plugin_info: PluginInfo) -> List[str]:
        """
        Validate that plugin dependencies are available.

        Args:
            plugin_info: Plugin metadata

        Returns:
            List of missing dependencies
        """
        missing = []

        for dependency in plugin_info.dependencies:
            # Check if dependency is a Python package
            try:
                importlib.import_module(dependency)
            except ImportError:
                missing.append(f"Python package: {dependency}")

        return missing

    def _load_plugin_module(self, plugin_info: PluginInfo) -> Optional[Any]:
        """
        Load a plugin module from its entry point.

        Args:
            plugin_info: Plugin metadata

        Returns:
            Loaded module or None if loading failed
        """
        entry_point = plugin_info.entry_point

        # Handle different entry point formats
        if entry_point.endswith('.py'):
            # Direct file path
            plugin_path = None

            # Search in plugin directories
            for directory in self.plugin_directories:
                candidate = Path(directory) / entry_point
                if candidate.exists():
                    plugin_path = candidate
                    break

            if not plugin_path:
                logger.error(f"Plugin file not found: {entry_point}")
                return None

            # Load the module
            spec = importlib.util.spec_from_file_location(plugin_info.name, plugin_path)
            if not spec or not spec.loader:
                logger.error(f"Could not create module spec for {plugin_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_info.name] = module

            try:
                spec.loader.exec_module(module)
                return module
            except Exception as e:
                logger.error(f"Error loading plugin module {plugin_path}: {e}")
                return None

        else:
            # Python module path
            try:
                return importlib.import_module(entry_point)
            except ImportError as e:
                logger.error(f"Could not import plugin module {entry_point}: {e}")
                return None

    def _find_plugin_class(self, module: Any, plugin_info: PluginInfo) -> Optional[Type[Plugin]]:
        """
        Find the plugin class in a loaded module.

        Args:
            module: Loaded plugin module
            plugin_info: Plugin metadata

        Returns:
            Plugin class if found, None otherwise
        """
        # Look for classes that inherit from Plugin
        from .plugin_registry import Plugin as BasePlugin

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                issubclass(attr, BasePlugin) and
                attr != BasePlugin):
                return attr

        # Fallback: look for a class with the plugin name
        plugin_class_name = plugin_info.name.replace('_', '').replace('-', '').title() + 'Plugin'
        if hasattr(module, plugin_class_name):
            plugin_class = getattr(module, plugin_class_name)
            if isinstance(plugin_class, type) and issubclass(plugin_class, BasePlugin):
                return plugin_class

        return None

    def _load_plugin_metadata(self, plugin_dir: Path) -> Optional[PluginInfo]:
        """
        Load plugin metadata from a plugin directory.

        Args:
            plugin_dir: Plugin directory path

        Returns:
            PluginInfo if metadata found, None otherwise
        """
        # Look for metadata files
        metadata_files = [
            plugin_dir / "plugin.json",
            plugin_dir / "plugin.yaml",
            plugin_dir / "plugin.yml",
            plugin_dir / "pyproject.toml"
        ]

        for metadata_file in metadata_files:
            if metadata_file.exists():
                try:
                    if metadata_file.suffix == '.json':
                        import json
                        with open(metadata_file, 'r') as f:
                            data = json.load(f)
                    elif metadata_file.suffix in ['.yaml', '.yml']:
                        import yaml
                        with open(metadata_file, 'r') as f:
                            data = yaml.safe_load(f)
                    elif metadata_file.name == 'pyproject.toml':
                        import tomllib
                        with open(metadata_file, 'rb') as f:
                            toml_data = tomllib.load(f)
                        data = toml_data.get('tool', {}).get('codomyrmex', {}).get('plugin', {})

                    # Extract plugin info
                    if all(key in data for key in ['name', 'version', 'entry_point']):
                        from .plugin_registry import PluginType

                        plugin_type = PluginType(data.get('plugin_type', 'utility'))
                        if isinstance(plugin_type, str):
                            plugin_type = PluginType(plugin_type)

                        return PluginInfo(
                            name=data['name'],
                            version=data['version'],
                            description=data.get('description', ''),
                            author=data.get('author', 'Unknown'),
                            plugin_type=plugin_type,
                            entry_point=data['entry_point'],
                            dependencies=data.get('dependencies', []),
                            config_schema=data.get('config_schema'),
                            homepage=data.get('homepage'),
                            license=data.get('license'),
                            tags=data.get('tags', [])
                        )

                except Exception as e:
                    logger.warning(f"Error loading metadata from {metadata_file}: {e}")

        return None

    def _load_plugin_metadata_from_file(self, plugin_file: Path) -> Optional[PluginInfo]:
        """
        Load plugin metadata from a single plugin file.

        Args:
            plugin_file: Plugin file path

        Returns:
            PluginInfo if metadata found, None otherwise
        """
        # For single-file plugins, extract metadata from docstring or comments
        try:
            with open(plugin_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for plugin metadata in comments or docstring
            metadata_match = re.search(r'#\s*plugin:\s*(\{.*\})', content, re.DOTALL)
            if metadata_match:
                import json
                metadata = json.loads(metadata_match.group(1))

                from .plugin_registry import PluginType

                plugin_type = PluginType(metadata.get('type', 'utility'))
                if isinstance(plugin_type, str):
                    plugin_type = PluginType(plugin_type)

                return PluginInfo(
                    name=metadata.get('name', plugin_file.stem),
                    version=metadata.get('version', '1.0.0'),
                    description=metadata.get('description', ''),
                    author=metadata.get('author', 'Unknown'),
                    plugin_type=plugin_type,
                    entry_point=str(plugin_file),
                    dependencies=metadata.get('dependencies', []),
                    tags=metadata.get('tags', [])
                )

        except Exception as e:
            logger.debug(f"Could not extract metadata from {plugin_file}: {e}")

        return None


# Convenience functions

def discover_plugins() -> List[PluginInfo]:
    """
    Convenience function to discover plugins.

    Returns:
        List of discovered PluginInfo objects
    """
    loader = PluginLoader()
    return loader.discover_plugins()


def load_plugin(plugin_info: PluginInfo, config: Optional[Dict[str, Any]] = None) -> LoadResult:
    """
    Convenience function to load a plugin.

    Args:
        plugin_info: Plugin metadata
        config: Plugin configuration

    Returns:
        LoadResult with loading outcome
    """
    loader = PluginLoader()
    return loader.load_plugin(plugin_info, config)


def unload_plugin(plugin_name: str) -> bool:
    """
    Convenience function to unload a plugin.

    Args:
        plugin_name: Name of the plugin

    Returns:
        True if successfully unloaded
    """
    loader = PluginLoader()
    return loader.unload_plugin(plugin_name)
