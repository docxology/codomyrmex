# Model Context Protocol -- Configuration Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the model_context_protocol module. Standardized LLM communication interfaces.

## Configuration Requirements

Before using model_context_protocol in any PAI workflow, ensure:

1. The module is importable via `from codomyrmex.model_context_protocol import *`
2. Any optional dependencies are installed (check with `codomyrmex check`)

## Agent Instructions

1. Import the module directly: `from codomyrmex.model_context_protocol import ...`
2. Check module availability with `list_modules()` from system_discovery
3. Available MCP tools: `inspect_server`, `list_registered_tools`, `get_tool_schema`
4. MCP server transport and discovery are configured at startup. Tool discovery uses a 5-minute TTL cache for auto-discovered modules.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("model_context_protocol.setting")

# Update configuration
set_config("model_context_protocol.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/model_context_protocol/AGENTS.md)
