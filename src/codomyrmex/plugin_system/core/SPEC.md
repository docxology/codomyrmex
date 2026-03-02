# Core - Technical Specification

## Overview

Three-layer plugin architecture: `PluginRegistry` for storage and lookup, `PluginLoader` for filesystem discovery and instantiation, and `PluginManager` for coordinated lifecycle management.

## Key Classes

### `PluginRegistry` (plugin_registry.py)

| Method | Parameters | Returns |
|--------|-----------|---------|
| `register` | `plugin: Plugin` | `bool` (False if duplicate) |
| `unregister` | `name: str` | `bool` |
| `get` | `name: str` | `Plugin \| None` |
| `get_plugin_info` | `name: str` | `PluginInfo \| None` |
| `list_plugins` | `plugin_type: PluginType \| None` | `list[PluginInfo]` |
| `check_dependencies` | `name: str` | `list[str]` (missing deps) |
| `initialize_all` | none | `dict[str, bool]` |
| `shutdown_all` | none | `dict[str, bool]` |
| `register_global_hook` | `name: str`, `signature`, `description` | `Hook` |
| `emit_global_hook` | `name: str`, `*args`, `**kwargs` | `list[Any]` |

Singleton: `get_registry()`.

### `PluginManager` (plugin_manager.py)

| Method | Parameters | Returns |
|--------|-----------|---------|
| `discover_plugins` | none | `list[PluginInfo]` |
| `load_plugin` | `name: str` | `LoadResult` |
| `unload_plugin` | `name: str` | `bool` |
| `reload_plugin` | `name: str` | `LoadResult` |
| `enable_plugin` / `disable_plugin` | `name: str` | `bool` |
| `get_plugin` | `name: str` | `Plugin \| None` |
| `list_plugins` | none | `list[PluginInfo]` |
| `get_system_status` | none | `dict[str, Any]` |
| `cleanup` | none | `None` |

Singleton: `get_plugin_manager()`.

### `PluginLoader` (plugin_loader.py)

| Method | Parameters | Returns |
|--------|-----------|---------|
| `discover_plugins` | none | `list[PluginInfo]` |
| `load_plugin` | `name: str` | `LoadResult` |
| `unload_plugin` | `name: str` | `bool` |
| `reload_plugin` | `name: str` | `LoadResult` |
| `validate_plugin_dependencies` | `info: PluginInfo` | `list[str]` (missing) |

Search paths: `plugins/`, `~/.codomyrmex/plugins/`. Metadata formats: `plugin.json`, `plugin.yaml`, `pyproject.toml`.

### `Plugin` (plugin_registry.py)

Base class with lifecycle: `initialize(config) -> bool`, `shutdown() -> bool`, `register_hook(name, handler)`, `emit_hook(name)`, `get_state() -> PluginState`, `set_config(config)`, `get_config()`.

### `PluginInfo` (plugin_registry.py)

Fields: `name`, `version`, `description`, `author`, `plugin_type` (PluginType), `entry_point`, `dependencies` (list[str]), `enabled`, `tags`, `config_schema`, `homepage`, `license`. Method: `to_dict()`.

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `dataclasses`, `enum`, `collections.abc` (stdlib)

## Constraints

- Duplicate plugin names are rejected at registration time.
- Hook handler exceptions are caught and logged -- they do not propagate to the emitter.
- Plugin state machine: UNLOADED -> INITIALIZING -> ACTIVE -> SHUTTING_DOWN -> UNLOADED.
