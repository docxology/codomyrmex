# Codomyrmex Agents — src/codomyrmex/plugin_system

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Plugin architecture and management system. Provides pluggable architecture for extending Codomyrmex functionality with dynamic plugin loading, plugin registration and discovery, plugin validation, lifecycle management, and dependency resolution.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `plugin_loader.py` – Dynamic plugin loading implementation
- `plugin_manager.py` – Plugin lifecycle and execution management
- `plugin_registry.py` – Plugin registration and discovery
- `plugin_validator.py` – Plugin validation and verification

## Key Classes and Functions

### PluginManager (`plugin_manager.py`)
- `PluginManager()` – Manager for plugin lifecycle and execution
- `load_plugin(plugin_path: str) -> Plugin` – Load a plugin from path
- `register_plugin(plugin: Plugin) -> None` – Register a plugin
- `unregister_plugin(plugin_id: str) -> bool` – Unregister a plugin
- `get_plugin(plugin_id: str) -> Optional[Plugin]` – Get a plugin by ID
- `list_plugins() -> List[Plugin]` – List all registered plugins
- `execute_plugin(plugin_id: str, action: str, **kwargs) -> Any` – Execute a plugin action

### PluginRegistry (`plugin_registry.py`)
- `PluginRegistry()` – Registry for plugin registration and discovery
- `register(plugin: Plugin) -> None` – Register a plugin
- `unregister(plugin_id: str) -> bool` – Unregister a plugin
- `get(plugin_id: str) -> Optional[Plugin]` – Get a plugin by ID
- `find_by_type(plugin_type: str) -> List[Plugin]` – Find plugins by type
- `discover_plugins(plugin_dir: str) -> List[Plugin]` – Discover plugins in directory

### PluginLoader (`plugin_loader.py`)
- `PluginLoader()` – Dynamic plugin loading
- `load_from_path(path: str) -> Plugin` – Load plugin from file path
- `load_from_module(module_name: str) -> Plugin` – Load plugin from Python module
- `validate_plugin(plugin: Plugin) -> bool` – Validate plugin structure

### PluginValidator (`plugin_validator.py`)
- `PluginValidator()` – Plugin validation and verification
- `validate(plugin: Plugin) -> ValidationResult` – Validate a plugin
- `check_dependencies(plugin: Plugin) -> bool` – Check plugin dependencies
- `verify_signature(plugin: Plugin) -> bool` – Verify plugin signature

### Plugin Interface
- `Plugin` (base class/interface) – Plugin interface that all plugins must implement:
  - `plugin_id: str` – Unique plugin identifier
  - `plugin_name: str` – Plugin name
  - `plugin_version: str` – Plugin version
  - `plugin_type: str` – Plugin type
  - `dependencies: List[str]` – Plugin dependencies
  - `execute(action: str, **kwargs) -> Any` – Execute plugin action

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation