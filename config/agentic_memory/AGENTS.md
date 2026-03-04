# Agentic Memory -- Configuration Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the agentic_memory module. Persistent, searchable agent memory with typed retrieval.

## Configuration Requirements

Before using agentic_memory in any PAI workflow, ensure:

1. The module is importable via `from codomyrmex.agentic_memory import *`
2. Any optional dependencies are installed (check with `codomyrmex check`)

## Agent Instructions

1. Import the module directly: `from codomyrmex.agentic_memory import ...`
2. Check module availability with `list_modules()` from system_discovery
3. Available MCP tools: `memory_put`, `memory_get`, `memory_search`
4. Memory storage defaults to in-memory. For persistent storage, configure a JSONFileStore with a file path. Obsidian vault integration requires a vault directory path.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("agentic_memory.setting")

# Update configuration
set_config("agentic_memory.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/agentic_memory/AGENTS.md)
