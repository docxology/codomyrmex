# Agent Guidelines - Plugin System

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

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
