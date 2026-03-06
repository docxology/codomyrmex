# Documents -- Configuration Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the documents module. Document I/O operations for multiple formats including markdown, JSON, PDF, YAML, XML, CSV, HTML, and plain text.

## Configuration Requirements

Before using documents in any PAI workflow, ensure:

1. `CODOMYRMEX_CACHE_DIR` is set -- Directory for document cache storage

## Agent Instructions

1. Verify required environment variables are set before invoking documents tools
2. Use `get_config("documents.<key>")` from config_management to read module settings
3. Available MCP tools: `documents_read`, `documents_write`, `documents_convert`
4. Cache directory defaults to system temp. Document format detection is automatic based on file extension.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("documents.setting")

# Update configuration
set_config("documents.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/documents/AGENTS.md)
