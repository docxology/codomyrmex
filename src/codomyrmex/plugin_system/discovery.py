"""Plugin discovery and lifecycle management.

Provides automatic plugin scanning via entry points and directory
scanning, with lifecycle hooks for initialization and teardown.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class PluginState(Enum):
    """Lifecycle state of a plugin."""

    DISCOVERED = "discovered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class PluginHook(Protocol):
    """Protocol for plugin lifecycle callbacks."""

    def on_load(self) -> None:
        """Called when the plugin module is loaded."""
        ...

    def on_init(self, config: dict[str, Any]) -> None:
        """Called when the plugin is initialized with config."""
        ...

    def on_teardown(self) -> None:
        """Called when the plugin is being deactivated."""
        ...


@dataclass
class PluginInfo:
    """Metadata about a discovered plugin.

    Attributes:
        name: Plugin identifier.
        module_path: Full dotted module path.
        version: Plugin version string.
        author: Plugin author.
        description: Brief description.
        state: Current lifecycle state.
        entry_point: Entry point group that discovered it.
        dependencies: List of required plugin names.
        error: Error message if state is ERROR.
        metadata: Additional plugin metadata.
    """

    name: str
    module_path: str
    version: str = "0.0.0"
    author: str = ""
    description: str = ""
    state: PluginState = PluginState.DISCOVERED
    entry_point: str = ""
    dependencies: list[str] = field(default_factory=list)
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscoveryResult:
    """Result of a plugin discovery scan.

    Attributes:
        plugins: List of discovered plugins.
        errors: List of (source, error_message) tuples.
        scan_sources: Sources that were scanned.
    """

    plugins: list[PluginInfo] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)
    scan_sources: list[str] = field(default_factory=list)


class PluginDiscovery:
    """Discovers plugins from entry points and directory scanning.

    Supports two discovery mechanisms:
    1. **Entry points**: Scans Python package metadata for a
       configurable entry point group.
    2. **Directory scanning**: Scans a directory for Python modules
       that contain a ``PLUGIN_INFO`` dict or a ``Plugin`` class.

    Example::

        discovery = PluginDiscovery(entry_point_group="codomyrmex.plugins")
        result = discovery.scan()
        for plugin in result.plugins:
            print(f"Found: {plugin.name} v{plugin.version}")
    """

    def __init__(
        self,
        entry_point_group: str = "codomyrmex.plugins",
        plugin_dirs: list[str] | None = None,
    ) -> None:
        """Initialize this instance."""
        self._entry_point_group = entry_point_group
        self._plugin_dirs = plugin_dirs or []

    def scan_entry_points(self) -> DiscoveryResult:
        """Discover plugins from installed package entry points.

        Returns:
            DiscoveryResult with plugins found via entry points.
        """
        result = DiscoveryResult(scan_sources=[f"entry_point:{self._entry_point_group}"])

        try:
            eps = importlib.metadata.entry_points()
            # Python 3.12+ returns a SelectableGroups; 3.9+ dict
            if hasattr(eps, "select"):
                group_eps = eps.select(group=self._entry_point_group)
            elif isinstance(eps, dict):
                group_eps = eps.get(self._entry_point_group, [])
            else:
                group_eps = [
                    ep for ep in eps if getattr(ep, "group", "") == self._entry_point_group
                ]

            for ep in group_eps:
                try:
                    info = PluginInfo(
                        name=ep.name,
                        module_path=ep.value if hasattr(ep, "value") else str(ep),
                        entry_point=self._entry_point_group,
                        state=PluginState.DISCOVERED,
                    )
                    result.plugins.append(info)
                except Exception as exc:
                    result.errors.append((ep.name, str(exc)))
        except Exception as exc:
            result.errors.append(("entry_points", str(exc)))

        return result

    def scan_directory(self, directory: str) -> DiscoveryResult:
        """Discover plugins by scanning a directory for Python modules.

        Looks for modules containing either:
        - A ``PLUGIN_INFO`` dict with ``name`` and ``version`` keys
        - A class named ``Plugin`` with a ``name`` attribute

        Args:
            directory: Absolute path to scan.

        Returns:
            DiscoveryResult with plugins found in the directory.
        """
        result = DiscoveryResult(scan_sources=[f"directory:{directory}"])

        if not os.path.isdir(directory):
            result.errors.append((directory, "Not a valid directory"))
            return result

        for filename in sorted(os.listdir(directory)):
            if not filename.endswith(".py") or filename.startswith("_"):
                continue

            module_name = filename[:-3]
            filepath = os.path.join(directory, filename)

            try:
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check for PLUGIN_INFO dict
                plugin_info_dict = getattr(module, "PLUGIN_INFO", None)
                if isinstance(plugin_info_dict, dict) and "name" in plugin_info_dict:
                    info = PluginInfo(
                        name=plugin_info_dict["name"],
                        module_path=filepath,
                        version=plugin_info_dict.get("version", "0.0.0"),
                        author=plugin_info_dict.get("author", ""),
                        description=plugin_info_dict.get("description", ""),
                        state=PluginState.DISCOVERED,
                        dependencies=plugin_info_dict.get("dependencies", []),
                    )
                    result.plugins.append(info)
                    continue

                # Check for Plugin class
                plugin_cls = getattr(module, "Plugin", None)
                if plugin_cls is not None and hasattr(plugin_cls, "name"):
                    info = PluginInfo(
                        name=getattr(plugin_cls, "name", module_name),
                        module_path=filepath,
                        version=getattr(plugin_cls, "version", "0.0.0"),
                        description=getattr(plugin_cls, "description", ""),
                        state=PluginState.DISCOVERED,
                    )
                    result.plugins.append(info)

            except Exception as exc:
                result.errors.append((filepath, str(exc)))

        return result

    def scan(self) -> DiscoveryResult:
        """Run full discovery: entry points + all configured directories.

        Returns:
            Combined DiscoveryResult from all sources.
        """
        combined = DiscoveryResult()

        ep_result = self.scan_entry_points()
        combined.plugins.extend(ep_result.plugins)
        combined.errors.extend(ep_result.errors)
        combined.scan_sources.extend(ep_result.scan_sources)

        for directory in self._plugin_dirs:
            dir_result = self.scan_directory(directory)
            combined.plugins.extend(dir_result.plugins)
            combined.errors.extend(dir_result.errors)
            combined.scan_sources.extend(dir_result.scan_sources)

        return combined
