# Plugin System Module Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Dynamic plugin loading, discovery, and lifecycle management with sandboxed execution.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **InterfaceEnforcer** — Validates that a plugin class implements a specific interface.
- **PluginError** — Base exception for plugin-related errors.
- **LoadError** — Raised when plugin loading fails.
- **DependencyError** — Raised when plugin dependency resolution fails.
- **HookError** — Raised when plugin hook operations fail.
- **PluginValidationError** — Raised when plugin validation fails.
- `discover_plugins()` — Convenience function to discover plugins.
- `load_plugin()` — Convenience function to load a plugin.
- `unload_plugin()` — Convenience function to unload a plugin.
- `get_plugin_manager()` — get_plugin_manager

## Quick Start

```python
from codomyrmex.plugin_system import InterfaceEnforcer, PluginError, LoadError

instance = InterfaceEnforcer()
```

## Source Files

- `enforcer.py`
- `exceptions.py`
- `plugin_loader.py`
- `plugin_manager.py`
- `plugin_registry.py`
- `plugin_validator.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k plugin_system -v
```

## Navigation

- **Source**: [src/codomyrmex/plugin_system/](../../../src/codomyrmex/plugin_system/)
- **Parent**: [Modules](../README.md)
