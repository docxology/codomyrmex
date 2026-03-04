# Calendar Integration -- Configuration Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the calendar_integration module. Calendar management with Google Calendar integration.

## Configuration Requirements

Before using calendar_integration in any PAI workflow, ensure:

1. `GOOGLE_CLIENT_ID` is set -- Google OAuth client ID for Calendar API
2. `GOOGLE_CLIENT_SECRET` is set -- Google OAuth client secret
3. `GOOGLE_REFRESH_TOKEN` is set -- Google OAuth refresh token for persistent access

## Agent Instructions

1. Verify required environment variables are set before invoking calendar_integration tools
2. Use `get_config("calendar_integration.<key>")` from config_management to read module settings
3. Available MCP tools: `calendar_list_events`, `calendar_create_event`, `calendar_get_event`, `calendar_delete_event`, `calendar_update_event`
4. Requires Google Cloud project with Calendar API enabled. OAuth credentials must be configured before use. Install with `uv sync --extra calendar`.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("calendar_integration.setting")

# Update configuration
set_config("calendar_integration.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/calendar_integration/AGENTS.md)
