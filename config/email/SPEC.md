# Email Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Email integration with Gmail and AgentMail providers. Provides generic EmailMessage and EmailProvider abstractions with inbox management, threading, and webhook support. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `AGENTMAIL_API_KEY` | string | Yes | None | API key for AgentMail service |
| `AGENTMAIL_DEFAULT_INBOX` | string | Yes | None | Default inbox ID for AgentMail operations |
| `GOOGLE_CLIENT_ID` | string | Yes | None | Google OAuth client ID for Gmail API |
| `GOOGLE_CLIENT_SECRET` | string | Yes | None | Google OAuth client secret for Gmail |
| `GOOGLE_REFRESH_TOKEN` | string | Yes | None | Google OAuth refresh token for Gmail access |

## Environment Variables

```bash
# Required
export AGENTMAIL_API_KEY=""    # API key for AgentMail service
export AGENTMAIL_DEFAULT_INBOX=""    # Default inbox ID for AgentMail operations
export GOOGLE_CLIENT_ID=""    # Google OAuth client ID for Gmail API
export GOOGLE_CLIENT_SECRET=""    # Google OAuth client secret for Gmail
export GOOGLE_REFRESH_TOKEN=""    # Google OAuth refresh token for Gmail access
```

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- `AGENTMAIL_API_KEY` must be set before module initialization
- `AGENTMAIL_DEFAULT_INBOX` must be set before module initialization
- `GOOGLE_CLIENT_ID` must be set before module initialization
- `GOOGLE_CLIENT_SECRET` must be set before module initialization
- `GOOGLE_REFRESH_TOKEN` must be set before module initialization
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/email/SPEC.md)
