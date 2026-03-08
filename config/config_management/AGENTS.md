# Config Management -- Configuration Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the config_management module. Central configuration management, validation, and deployment for the Codomyrmex ecosystem.

## Configuration Requirements

Before using config_management in any PAI workflow, ensure:

1. `ENVIRONMENT` is set (default: `development`) -- Active environment name (development, staging, production)
2. `OLLAMA_BASE_URL` is set (default: `http://localhost:11434`) -- Base URL for Ollama LLM service

## Agent Instructions

1. Verify required environment variables are set before invoking config_management tools
2. Use `get_config("config_management.<key>")` from config_management to read module settings
3. Available MCP tools: `get_config`, `set_config`, `validate_config`
4. Configuration is loaded from YAML files, environment variables, and programmatic defaults. Environment variables take precedence over file values.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("config_management.setting")

# Update configuration
set_config("config_management.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/config_management/AGENTS.md)
