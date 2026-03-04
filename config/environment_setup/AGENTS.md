# Environment Setup -- Configuration Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the environment_setup module. Environment validation, dependency checking, and uv package manager integration.

## Configuration Requirements

Before using environment_setup in any PAI workflow, ensure:

1. `VIRTUAL_ENV` is set -- Path to active virtual environment (auto-detected)
2. `UV_ACTIVE` is set (default: `1`) -- Indicator that uv environment is active
3. `CONDA_DEFAULT_ENV` is set -- Active Conda environment name

## Agent Instructions

1. Verify required environment variables are set before invoking environment_setup tools
2. Use `get_config("environment_setup.<key>")` from config_management to read module settings
3. This module has no auto-discovered MCP tools; use direct Python imports
4. Environment validation runs automatically on import. API key checks use a configurable list of required keys per module.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("environment_setup.setting")

# Update configuration
set_config("environment_setup.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/environment_setup/AGENTS.md)
