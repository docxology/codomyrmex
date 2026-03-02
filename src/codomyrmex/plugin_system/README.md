# Plugin System Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

Extensible plugin architecture for third-party modules.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Discover available plugins and extensions | `plugin_scan_entry_points` |
| **PLAN** | Resolve plugin dependencies for task execution | `plugin_resolve_dependencies` |
| **EXECUTE** | Load and invoke discovered plugins | `plugin_scan_entry_points`, `plugin_resolve_dependencies` |

PAI agents use plugin_system to discover and load available capabilities at runtime. The Architect agent calls `plugin_scan_entry_points` during OBSERVE to map available tools; the Engineer resolves dependencies before EXECUTE.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`InterfaceEnforcer`** — Validates that a plugin class implements a specific interface.
- **`PluginError`** — Base exception for plugin-related errors.
- **`LoadError`** — Raised when plugin loading fails.
- **`DependencyError`** — Raised when plugin dependency resolution fails.
- **`HookError`** — Raised when plugin hook operations fail.
- **`PluginValidationError`** — Raised when plugin validation fails.
- **`PluginStateError`** — Raised when plugin state operations fail.
- **`PluginConflictError`** — Raised when plugin conflicts are detected.

## Quick Start

```python
from codomyrmex.plugin_system import (
    PluginManager, PluginLoader, PluginRegistry, Plugin, PluginInfo
)

# Initialize plugin manager
manager = PluginManager()

# Load plugins from directory
manager.load_plugins_from("./plugins")

# List loaded plugins
for plugin in manager.list_plugins():
    print(f"{plugin.name} v{plugin.version}: {plugin.description}")

# Get and use a plugin
plugin = manager.get_plugin("my_plugin")
plugin.activate()
result = plugin.execute(data)
plugin.deactivate()
```

## Creating Plugins

```python
from codomyrmex.plugin_system import Plugin, PluginInfo

@PluginInfo(name="my_plugin", version="1.0.0")
class MyPlugin(Plugin):
    def activate(self):
        print("Plugin activated")

    def execute(self, data):
        return process(data)

    def deactivate(self):
        print("Plugin deactivated")
```

## Exports

| Class | Description |
|-------|-------------|
| `PluginManager` | Load, activate, deactivate plugins |
| `PluginLoader` | Load plugins from paths |
| `PluginRegistry` | Register and discover plugins |
| `PluginValidator` | Validate plugin structure |
| `Plugin` | Base plugin class |
| `PluginInfo` | Plugin metadata decorator |
| `PluginType` | Enum for plugin categories |
| `PluginState` | Enum: loaded, active, inactive, error |
| `PluginError` | Base plugin exception |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k plugin_system -v
```

## Documentation

- [Module Documentation](../../../docs/modules/plugin_system/README.md)
- [Agent Guide](../../../docs/modules/plugin_system/AGENTS.md)
- [Specification](../../../docs/modules/plugin_system/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
