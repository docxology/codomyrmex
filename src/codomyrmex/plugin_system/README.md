# Plugin System

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview
The `plugin_system` module enables the extensibility of the Codomyrmex platform. It allows users and developers to add new capabilities—such as custom agent providers, new document parsers, or additional CLI commands—without modifying the core codebase. This module handles the discovery, validation, loading, and lifecycle management of these extensions.

## Key Features
- **Dynamic Discovery**: The `plugin_loader.py` can find plugins in user-configured directories or Python packages.
- **Strict Validation**: The `plugin_validator.py` ensures that loaded plugins conform to required interfaces and metadata standards.
- **Centralized Registry**: The `plugin_registry.py` maintains the state of all active plugins and resolves dependencies.
- **Lifecycle Management**: The `plugin_manager.py` handles initialization, activation, and graceful shutdown of plugins.

## Quick Start

```python
from codomyrmex.plugin_system.plugin_manager import PluginManager

# Initialize manager
manager = PluginManager(plugin_dirs=["./my_plugins"])

# Discover and load
manager.discover_plugins()
manager.load_all()

# Access a plugin extension point
formatter = manager.get_extension("text_formatter", "custom_markdown")
result = formatter.format(text)
```

## Module Structure

- `plugin_loader.py`: Scans directories and entry points for plugin artifacts.
- `plugin_validator.py`: Checks plugin schemas and interface compliance.
- `plugin_registry.py`: Stores loaded plugin references.
- `plugin_manager.py`: High-level orchestration of the plugin system.

## Navigation Links
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [README](../../../README.md)
