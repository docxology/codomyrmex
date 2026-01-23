# Codomyrmex Agents — src/codomyrmex/plugin_system

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Plugin System module provides a comprehensive plugin architecture for extending Codomyrmex functionality through third-party plugins. It supports plugin discovery, validation, loading, lifecycle management, dependency resolution, security scanning, and hook-based event systems for inter-plugin communication.

## Active Components

### Core Infrastructure

- `plugin_manager.py` - Central plugin management interface
  - Key Classes: `PluginManager`
  - Key Functions: `discover_plugins()`, `load_plugin()`, `unload_plugin()`, `enable_plugin()`, `disable_plugin()`
- `plugin_loader.py` - Plugin loading and initialization
  - Key Classes: `PluginLoader`, `LoadResult`
  - Key Functions: `discover_plugins()`, `load_plugin()`, `unload_plugin()`, `reload_plugin()`
- `plugin_registry.py` - Plugin registration and metadata
  - Key Classes: `PluginRegistry`, `Plugin`, `PluginInfo`, `PluginType`, `PluginState`, `Hook`
  - Key Functions: `register()`, `unregister()`, `get()`, `list_plugins()`
- `plugin_validator.py` - Plugin validation and security scanning
  - Key Classes: `PluginValidator`, `ValidationResult`
  - Key Functions: `validate()`, `validate_plugin()`, `validate_plugin_metadata()`, `check_plugin_dependencies()`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `PluginManager` | plugin_manager | Central orchestration of plugin lifecycle |
| `PluginLoader` | plugin_loader | Dynamic plugin loading and initialization |
| `PluginRegistry` | plugin_registry | Plugin registration and lookup |
| `Plugin` | plugin_registry | Base class for all plugins |
| `PluginInfo` | plugin_registry | Plugin metadata container |
| `PluginType` | plugin_registry | Enum for plugin categories (ANALYZER, FORMATTER, etc.) |
| `PluginState` | plugin_registry | Enum for lifecycle states (ACTIVE, DISABLED, ERROR, etc.) |
| `PluginValidator` | plugin_validator | Security and compatibility validation |
| `ValidationResult` | plugin_validator | Validation outcome with issues/warnings |
| `LoadResult` | plugin_loader | Loading operation result |
| `Hook` | plugin_registry | Event hook for plugin communication |
| `discover_plugins()` | plugin_manager | Find available plugins in directories |
| `load_plugin()` | plugin_manager | Load and initialize a plugin |
| `unload_plugin()` | plugin_manager | Unload a running plugin |
| `reload_plugin()` | plugin_loader | Reload a plugin with new config |
| `enable_plugin()` | plugin_manager | Activate a disabled plugin |
| `disable_plugin()` | plugin_manager | Deactivate a running plugin |
| `register_hook()` | plugin_manager | Register global event hooks |
| `emit_hook()` | plugin_manager | Emit events to registered handlers |
| `get_plugin_status()` | plugin_manager | Query plugin state and metadata |
| `get_system_status()` | plugin_manager | Overall plugin system health |
| `validate_plugin()` | plugin_validator | Security scan and validation |
| `get_plugin_manager()` | plugin_manager | Get singleton manager instance |
| `get_registry()` | plugin_registry | Get global registry instance |

## Operating Contracts

1. **Logging**: All operations use `logging_monitoring` for structured logging
2. **Plugin Discovery**: Searches configured directories for plugin.json, plugin.yaml, or pyproject.toml
3. **Security Scanning**: Validates plugins for dangerous patterns (eval, exec, subprocess, etc.)
4. **Lifecycle States**: Plugins transition through UNLOADED -> LOADING -> INITIALIZING -> ACTIVE
5. **Dependency Resolution**: Validates plugin dependencies before loading
6. **Hook System**: Global hooks enable cross-plugin communication

## Plugin Types

| Type | Purpose |
| :--- | :--- |
| `ANALYZER` | Code analysis plugins |
| `FORMATTER` | Code formatting plugins |
| `EXPORTER` | Data export plugins |
| `IMPORTER` | Data import plugins |
| `PROCESSOR` | Data processing plugins |
| `HOOK` | Event hook plugins |
| `UTILITY` | General utility plugins |
| `ADAPTER` | Integration adapters |
| `AGENT` | AI agent plugins |

## Integration Points

- **logging_monitoring** - Structured logging for all operations
- **agents** - Agent plugins extend the agents module
- **coding** - Code analysis and formatting plugins

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| agents | [../agents/AGENTS.md](../agents/AGENTS.md) | AI agent integration |
| coding | [../coding/AGENTS.md](../coding/AGENTS.md) | Code execution and analysis |
| security | [../security/AGENTS.md](../security/AGENTS.md) | Security scanning |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
