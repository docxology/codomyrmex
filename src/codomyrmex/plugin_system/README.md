# Plugin System Module

**Version**: v0.1.0 | **Status**: Active

Extensible plugin architecture for third-party modules.


## Installation

```bash
pip install codomyrmex
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
