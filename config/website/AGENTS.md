# Website -- Configuration Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the website module. Web application server for the Codomyrmex platform.

## Configuration Requirements

Before using website in any PAI workflow, ensure:

1. `CODOMYRMEX_CORS_ORIGINS` is set (default: `*`) -- Allowed CORS origins (comma-separated)
2. `CODOMYRMEX_ENV` is set (default: `Development`) -- Application environment name
3. `CODOMYRMEX_OLLAMA_URL` is set (default: `http://localhost:11434`) -- Ollama service URL for web LLM features
4. `CODOMYRMEX_DEFAULT_MODEL` is set (default: `llama3.2:1b`) -- Default Ollama model for web interface

## Agent Instructions

1. Verify required environment variables are set before invoking website tools
2. Use `get_config("website.<key>")` from config_management to read module settings
3. This module has no auto-discovered MCP tools; use direct Python imports
4. CORS origins control cross-origin access. Ollama URL must point to a running Ollama instance for LLM features.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("website.setting")

# Update configuration
set_config("website.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/website/AGENTS.md)
