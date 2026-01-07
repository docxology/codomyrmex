# plugin_system

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Plugin architecture and management system. Provides pluggable architecture for extending Codomyrmex functionality with dynamic plugin loading, plugin registration and discovery, plugin validation, lifecycle management, and dependency resolution.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `plugin_loader.py` – File
- `plugin_manager.py` – File
- `plugin_registry.py` – File
- `plugin_validator.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.plugin_system import (
    PluginManager,
    PluginLoader,
    PluginRegistry,
)

# Initialize plugin manager
plugin_mgr = PluginManager()

# Load plugin
loader = PluginLoader()
plugin = loader.load_plugin("path/to/plugin.py")

# Register plugin
registry = PluginRegistry()
registry.register(plugin)

# Use plugin
plugin_mgr.activate_plugin(plugin.name)
result = plugin_mgr.execute_plugin(plugin.name, action="process", data={...})

# List available plugins
plugins = plugin_mgr.list_plugins()
print(f"Available plugins: {[p.name for p in plugins]}")
```

