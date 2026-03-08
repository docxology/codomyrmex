# Testing -- Configuration Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the testing module. Testing infrastructure and utilities for the Codomyrmex test suite.

## Configuration Requirements

Before using testing in any PAI workflow, ensure:

1. `CODOMYRMEX_TEST_MODE` is set (default: `true`) -- Enables test mode for safe execution

## Agent Instructions

1. Verify required environment variables are set before invoking testing tools
2. Use `get_config("testing.<key>")` from config_management to read module settings
3. This module has no auto-discovered MCP tools; use direct Python imports
4. Test mode is automatically enabled when running under pytest. Test markers (unit, integration, slow, etc.) are defined in pytest.ini.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("testing.setting")

# Update configuration
set_config("testing.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/testing/AGENTS.md)
