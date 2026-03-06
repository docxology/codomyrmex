# Coding -- Configuration Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the coding module. Unified module for code execution, sandboxing, review, monitoring, and debugging.

## Configuration Requirements

Before using coding in any PAI workflow, ensure:

1. The module is importable via `from codomyrmex.coding import *`
2. Any optional dependencies are installed (check with `codomyrmex check`)

## Agent Instructions

1. Import the module directly: `from codomyrmex.coding import ...`
2. Check module availability with `list_modules()` from system_discovery
3. Available MCP tools: `code_execute`, `code_list_languages`, `code_review_file`, `code_review_project`, `code_debug`
4. Code execution runs in sandboxed environments with configurable resource limits (CPU, memory, timeout). Review uses static analysis rules.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("coding.setting")

# Update configuration
set_config("coding.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/coding/AGENTS.md)
