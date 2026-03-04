# Email Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Email integration with Gmail and AgentMail providers. Provides generic EmailMessage and EmailProvider abstractions with inbox management, threading, and webhook support.

## Quick Configuration

```bash
export AGENTMAIL_API_KEY=""    # API key for AgentMail service (required)
export AGENTMAIL_DEFAULT_INBOX=""    # Default inbox ID for AgentMail operations (required)
export GOOGLE_CLIENT_ID=""    # Google OAuth client ID for Gmail API (required)
export GOOGLE_CLIENT_SECRET=""    # Google OAuth client secret for Gmail (required)
export GOOGLE_REFRESH_TOKEN=""    # Google OAuth refresh token for Gmail access (required)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `AGENTMAIL_API_KEY` | str | None | API key for AgentMail service |
| `AGENTMAIL_DEFAULT_INBOX` | str | None | Default inbox ID for AgentMail operations |
| `GOOGLE_CLIENT_ID` | str | None | Google OAuth client ID for Gmail API |
| `GOOGLE_CLIENT_SECRET` | str | None | Google OAuth client secret for Gmail |
| `GOOGLE_REFRESH_TOKEN` | str | None | Google OAuth refresh token for Gmail access |

## MCP Tools

This module exposes 12 MCP tool(s):

- `agentmail_send_message`
- `agentmail_list_messages`
- `agentmail_get_message`
- `agentmail_reply_to_message`
- `agentmail_list_inboxes`
- `agentmail_create_inbox`
- `agentmail_list_threads`
- `agentmail_create_webhook`
- `gmail_send_message`
- `gmail_list_messages`
- `gmail_get_message`
- `gmail_create_draft`

## PAI Integration

PAI agents invoke email tools through the MCP bridge. AgentMail requires an API key. Gmail requires Google OAuth credentials. Install with `uv sync --extra email`.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep email

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/email/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
