# Core - Agent Coordination

## Purpose

Plugin lifecycle management system providing registration, loading, dependency resolution, and hook-based extension for the Codomyrmex platform.

## Key Components

| Component | Role |
|-----------|------|
| `PluginRegistry` | Central registry for plugin instances with category tracking and global hooks |
| `PluginManager` | High-level manager coordinating registry, validator, and loader |
| `PluginLoader` | Discovery and loading from `plugins/` and `~/.codomyrmex/plugins/` directories |
| `Plugin` | Base class for all plugins with lifecycle methods and hook support |
| `PluginInfo` | Dataclass: name, version, description, author, plugin_type, entry_point, dependencies |
| `PluginType` | Enum: ANALYZER, FORMATTER, EXPORTER, IMPORTER, PROCESSOR, HOOK, UTILITY, ADAPTER, AGENT |
| `PluginState` | Enum: 10 lifecycle states from UNKNOWN to UNLOADED |
| `Hook` | Named hook with handler list and `emit()` method |
| `LoadResult` | Dataclass: plugin_name, success, plugin_instance, error_message, warnings |

## Operating Contracts

- `PluginRegistry.register()` rejects duplicate plugin names (logs warning, returns False).
- `Plugin.initialize(config)` transitions state to ACTIVE; `shutdown()` transitions to SHUTTING_DOWN.
- `PluginLoader` searches both local `plugins/` and user-global `~/.codomyrmex/plugins/` directories.
- Plugin metadata may come from `plugin.json`, `plugin.yaml`, or `pyproject.toml`.
- `PluginManager` is a singleton via `get_plugin_manager()`.
- `PluginRegistry` is a singleton via `get_registry()`.
- `check_dependencies(name)` returns list of missing dependency names.
- Hook `emit()` catches and logs exceptions from individual handlers without propagating.

## Integration Points

- **Parent module**: `plugin_system/` exposes `plugin_scan_entry_points` and `plugin_resolve_dependencies` MCP tools.
- **Global hooks**: `register_global_hook()` and `emit_global_hook()` for cross-plugin events.

## Navigation

- **Parent**: [plugin_system/](../README.md)
- **Sibling**: [SPEC.md](SPEC.md)
- **Root**: [/README.md](../../../../README.md)
