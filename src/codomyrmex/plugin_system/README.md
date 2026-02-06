# Plugin System Module

**Version**: v0.1.0 | **Status**: Active

Extensible plugin architecture for third-party modules.

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

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
