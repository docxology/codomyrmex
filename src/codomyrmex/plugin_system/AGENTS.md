# Agent Guidelines - Plugin System

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Extensible plugin architecture for third-party module extensions. Provides `PluginManager` for
loading, activating, and deactivating plugins, `PluginLoader` for path-based discovery, and
`PluginRegistry` for cross-module plugin sharing. Two MCP tools (`plugin_scan_entry_points`,
`plugin_resolve_dependencies`) expose discovery and dependency resolution.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `PluginManager`, `PluginLoader`, `PluginRegistry`, `PluginValidator`, `Plugin`, `PluginError` |
| `plugin_manager.py` | `PluginManager` — load, activate, deactivate, get, list plugins |
| `plugin_loader.py` | `PluginLoader` — load plugins from filesystem paths |
| `plugin_registry.py` | `PluginRegistry` — register and discover plugins |
| `plugin_validator.py` | `PluginValidator` — validate plugin structure before loading |
| `base.py` | `Plugin` — base plugin class with lifecycle hooks |
| `mcp_tools.py` | MCP tools: `plugin_scan_entry_points`, `plugin_resolve_dependencies` |

## Key Classes

- **PluginManager** — Load, activate, deactivate plugins
- **PluginLoader** — Load plugins from paths
- **PluginRegistry** — Register and discover plugins
- **PluginValidator** — Validate plugin structure
- **Plugin** — Base plugin class

## Agent Instructions

1. **Validate before load** — Use `PluginValidator` to check plugins
2. **Handle dependencies** — Check plugin dependencies before activation
3. **Lifecycle order** — Always: load → activate → use → deactivate
4. **Catch plugin errors** — Wrap plugin calls in try/except
5. **Use registry** — Register plugins for discovery by other modules

## Common Patterns

```python
from codomyrmex.plugin_system import PluginManager, PluginError

manager = PluginManager()

# Load all plugins
try:
    manager.load_plugins_from("./plugins")
except PluginError as e:
    log.error(f"Plugin load failed: {e}")

# Use a plugin safely
plugin = manager.get_plugin("my_plugin")
if plugin:
    try:
        plugin.activate()
        result = plugin.execute(data)
    except PluginError as e:
        log.error(f"Plugin error: {e}")
    finally:
        plugin.deactivate()
```

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `plugin_scan_entry_points` | Scan for installed plugins via Python package entry points | SAFE |
| `plugin_resolve_dependencies` | Resolve plugin dependencies and produce a topological load order | SAFE |

## Operating Contracts

- Always validate with `PluginValidator` before `PluginManager.load_plugins_from()` in production
- Lifecycle order is strictly: `load()` → `activate()` → use → `deactivate()` — skipping steps raises errors
- `PluginManager.get_plugin(name)` returns `None` if not found — always check before calling `activate()`
- `plugin_resolve_dependencies` returns a topologically sorted list — use this order for loading
- **DO NOT** catch `PluginError` and silently continue — always log or re-raise

## Testing Patterns

```python
# Verify plugin loading
manager = PluginManager()
manager.load_plugins_from("tests/fixtures/plugins")
assert len(manager.list_plugins()) > 0

# Verify plugin lifecycle
plugin = manager.get_plugin("test_plugin")
plugin.activate()
assert plugin.state == PluginState.ACTIVE
plugin.deactivate()
assert plugin.state == PluginState.INACTIVE
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `plugin_scan_entry_points`, `plugin_resolve_dependencies` | TRUSTED |
| **Architect** | Read + Design | `plugin_scan_entry_points`, `plugin_resolve_dependencies` — plugin architecture design | OBSERVED |
| **QATester** | Validation | `plugin_scan_entry_points` — plugin discovery verification, dependency graph validation | OBSERVED |
| **Researcher** | Read-only | `plugin_scan_entry_points`, `plugin_resolve_dependencies` — inspect plugin catalog | SAFE |

### Engineer Agent
**Use Cases**: Scanning for available plugins during OBSERVE, resolving plugin dependencies before BUILD, managing plugin registry.

### Architect Agent
**Use Cases**: Designing plugin interfaces, reviewing dependency graphs, planning plugin extension points.

### QATester Agent
**Use Cases**: Verifying plugin discovery during VERIFY, confirming dependency resolution correctness.

### Researcher Agent
**Use Cases**: Inspecting available plugin catalog and dependency resolution for research analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
