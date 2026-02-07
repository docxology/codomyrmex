# System Discovery Module — Agent Coordination

## Purpose

This module provides system discovery and orchestration capabilities

## Key Capabilities

- System Discovery operations and management

## Agent Usage Patterns

```python
from codomyrmex.system_discovery import *

# Agent uses system discovery capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/system_discovery/](../../../src/codomyrmex/system_discovery/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`FunctionCapability`** — Metadata about a discovered function capability.
- **`ClassCapability`** — Metadata about a discovered class capability.
- **`ModuleCapability`** — Aggregated capability information for a module.
- **`CapabilityScanner`** — Advanced capability scanner for the Codomyrmex ecosystem.
- **`ModuleInfo`** — Aggregated metadata and capabilities for a single discovered Codomyrmex module.
- **`get_system_context()`** — Get the current system context for agents.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k system_discovery -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
