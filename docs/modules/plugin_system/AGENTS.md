# Plugin System Module — Agent Coordination

## Purpose

Plugin System for Codomyrmex

## Key Capabilities

- Plugin System operations and management

## Agent Usage Patterns

```python
from codomyrmex.plugin_system import *

# Agent uses plugin system capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/plugin_system/](../../../src/codomyrmex/plugin_system/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`InterfaceEnforcer`** — Validates that a plugin class implements a specific interface.
- **`PluginError`** — Base exception for plugin-related errors.
- **`LoadError`** — Raised when plugin loading fails.
- **`DependencyError`** — Raised when plugin dependency resolution fails.
- **`HookError`** — Raised when plugin hook operations fail.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k plugin_system -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
