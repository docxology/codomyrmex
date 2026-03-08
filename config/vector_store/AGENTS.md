# Vector Store -- Configuration Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the vector_store module. Vector database integration for embedding storage and similarity search.

## Configuration Requirements

Before using vector_store in any PAI workflow, ensure:

1. The module is importable via `from codomyrmex.vector_store import *`
2. Any optional dependencies are installed (check with `codomyrmex check`)

## Agent Instructions

1. Import the module directly: `from codomyrmex.vector_store import ...`
2. Check module availability with `list_modules()` from system_discovery
3. This module has no auto-discovered MCP tools; use direct Python imports
4. Vector dimensions, distance metric (cosine, euclidean, dot product), and index type are set at store creation time.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("vector_store.setting")

# Update configuration
set_config("vector_store.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/vector_store/AGENTS.md)
