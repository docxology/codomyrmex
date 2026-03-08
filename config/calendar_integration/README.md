# Calendar Integration Configuration

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Calendar management with Google Calendar integration. Provides generic CalendarEvent and CalendarProvider abstractions with a GoogleCalendar implementation.

## Quick Configuration

```bash
export GOOGLE_CLIENT_ID=""    # Google OAuth client ID for Calendar API (required)
export GOOGLE_CLIENT_SECRET=""    # Google OAuth client secret (required)
export GOOGLE_REFRESH_TOKEN=""    # Google OAuth refresh token for persistent access (required)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `GOOGLE_CLIENT_ID` | str | None | Google OAuth client ID for Calendar API |
| `GOOGLE_CLIENT_SECRET` | str | None | Google OAuth client secret |
| `GOOGLE_REFRESH_TOKEN` | str | None | Google OAuth refresh token for persistent access |

## MCP Tools

This module exposes 5 MCP tool(s):

- `calendar_list_events`
- `calendar_create_event`
- `calendar_get_event`
- `calendar_delete_event`
- `calendar_update_event`

## PAI Integration

PAI agents invoke calendar_integration tools through the MCP bridge. Requires Google Cloud project with Calendar API enabled. OAuth credentials must be configured before use. Install with `uv sync --extra calendar`.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep calendar_integration

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/calendar_integration/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
