# Documentation -- Configuration Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the documentation module. Documentation management, quality auditing, and website generation.

## Configuration Requirements

Before using documentation in any PAI workflow, ensure:

1. `DOCS_PORT` is set (default: `3000`) -- Port for documentation dev server
2. `DOCS_HOST` is set (default: `localhost`) -- Host for documentation dev server

## Agent Instructions

1. Verify required environment variables are set before invoking documentation tools
2. Use `get_config("documentation.<key>")` from config_management to read module settings
3. Available MCP tools: `generate_module_docs`, `audit_rasp_compliance`
4. Documentation website runs on configurable host and port. Quality thresholds for RASP compliance can be adjusted in audit configuration.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("documentation.setting")

# Update configuration
set_config("documentation.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/documentation/AGENTS.md)
