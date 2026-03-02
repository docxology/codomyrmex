# Agent Guidelines - Plugin System

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Extensible plugin architecture for third-party modules.

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

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Key Parameters | Trust Level |
|------|-------------|----------------|-------------|
| `plugin_scan_entry_points` | Scan for installed plugins via Python package entry points | `entry_point_group` (default "codomyrmex.plugins") | Safe |
| `plugin_resolve_dependencies` | Resolve plugin dependencies and produce a topological load order | `plugins` (list of dicts with name and dependencies) | Safe |

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

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `plugin_scan_entry_points`, `plugin_resolve_dependencies`; full plugin lifecycle | TRUSTED |
| **Architect** | Read + Design | `plugin_scan_entry_points`, `plugin_resolve_dependencies`; plugin architecture design | OBSERVED |
| **QATester** | Validation | `plugin_scan_entry_points`; plugin discovery verification, dependency graph validation | OBSERVED |

### Engineer Agent
**Use Cases**: Scanning for available plugins during OBSERVE, resolving plugin dependencies before BUILD, managing plugin registry.

### Architect Agent
**Use Cases**: Designing plugin interfaces, reviewing dependency graphs, planning plugin extension points.

### QATester Agent
**Use Cases**: Verifying plugin discovery during VERIFY, confirming dependency resolution correctness.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
