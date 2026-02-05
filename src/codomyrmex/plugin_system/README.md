# plugin_system

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Plugin architecture for extending Codomyrmex functionality through third-party plugins. Provides a complete plugin lifecycle: discovery from configurable directories, validation for security and compatibility, dynamic loading with dependency resolution, and a central registry that tracks plugin state through registration, loading, activation, disabling, and shutdown phases. Supports nine plugin types including analyzers, formatters, exporters, processors, hooks, agents, and adapters.

## Key Exports

### Core Classes
- **`PluginManager`** -- Central management interface that coordinates discovery, validation, loading, and lifecycle of all plugins through its internal registry, validator, and loader
- **`PluginValidator`** -- Validates plugins for security compliance, API compatibility, and structural correctness before loading
- **`PluginLoader`** -- Discovers plugins from configured directories and handles dynamic module import and initialization
- **`PluginRegistry`** -- In-memory registry that stores and retrieves plugin metadata and state, supports lookup by name, type, and tags
- **`PluginInfo`** -- Dataclass holding plugin metadata: name, version, description, author, type, entry point, dependencies, tags, and config schema
- **`Plugin`** -- Base plugin class that plugins must extend to integrate with the system
- **`PluginType`** -- Enum defining plugin categories: analyzer, formatter, exporter, importer, processor, hook, utility, adapter, agent
- **`PluginState`** -- Enum for plugin lifecycle states: unknown, registered, loading, loaded, initializing, active, disabled, error, shutting_down, unloaded

### Exceptions
- **`PluginError`** -- Base exception for plugin operations, includes plugin_name and plugin_version context
- **`LoadError`** -- Raised when plugin loading fails (import errors, entry point resolution, initialization)
- **`DependencyError`** -- Raised when plugin dependencies cannot be resolved or are incompatible
- **`HookError`** -- Raised when plugin hook registration or execution fails
- **`PluginValidationError`** -- Raised when a plugin fails security or compatibility validation
- **`PluginStateError`** -- Raised for invalid state transitions in the plugin lifecycle
- **`PluginConflictError`** -- Raised when plugins conflict with each other (duplicate names, incompatible hooks)

## Directory Contents

- `plugin_manager.py` -- PluginManager class coordinating discovery, validation, loading, and lifecycle
- `plugin_registry.py` -- PluginRegistry, PluginInfo, Plugin base class, PluginType and PluginState enums, Hook class
- `plugin_validator.py` -- PluginValidator for security and compatibility checks
- `plugin_loader.py` -- PluginLoader for directory scanning and dynamic module import
- `enforcer.py` -- Plugin policy enforcement and constraint checking
- `exceptions.py` -- Full exception hierarchy for plugin system errors

## Navigation

- **Full Documentation**: [docs/modules/plugin_system/](../../../docs/modules/plugin_system/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
