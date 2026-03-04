# Database Management -- Configuration Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the database_management module. Database management, migration, backup, and administration.

## Configuration Requirements

Before using database_management in any PAI workflow, ensure:

1. `DB_HOST` is set (default: `localhost`) -- Database server hostname
2. `DB_PORT` is set (default: `5432`) -- Database server port
3. `DB_USER` is set (default: `postgres`) -- Database username

## Agent Instructions

1. Verify required environment variables are set before invoking database_management tools
2. Use `get_config("database_management.<key>")` from config_management to read module settings
3. This module has no auto-discovered MCP tools; use direct Python imports
4. Connection parameters can be set via environment variables or passed directly to DatabaseManager. Connection pooling size and timeout are configurable.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("database_management.setting")

# Update configuration
set_config("database_management.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/database_management/AGENTS.md)
