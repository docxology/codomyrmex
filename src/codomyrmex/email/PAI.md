# Personal AI Infrastructure — Email Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Email module provides email composition, sending, and management through a provider-abstracted interface. It supports multiple email protocols and providers with a unified API for drafting, sending, and reading messages.

## PAI Capabilities

### Email Operations

```python
from codomyrmex.email import AgentMailProvider, EmailDraft, AGENTMAIL_AVAILABLE

# AgentMail (requires AGENTMAIL_API_KEY env var)
if AGENTMAIL_AVAILABLE:
    provider = AgentMailProvider()
    draft = EmailDraft(
        to=["team@example.com"],
        subject="Sprint Summary",
        body_text="Completed PAI.md enrichment across 40+ modules."
    )
    sent = provider.send_message(draft)
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `EmailAddress` | Class | Email address data model |
| `EmailDraft` | Class | Outgoing email composition |
| `EmailMessage` | Class | Complete email message (sent/received) |
| `EmailProvider` | Class | Abstract email provider interface |
| `cli_commands` | Function | CLI commands for email operations |

## PAI Algorithm Phase Mapping

| Phase | Email Contribution |
|-------|---------------------|
| **EXECUTE** | Send notifications, reports, and alerts |
| **LEARN** | Archive sent/received emails for reference |

## MCP Tools

Twelve tools are auto-discovered via `@mcp_tool` and available through the PAI MCP bridge.

### AgentMail Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `agentmail_send_message` | Send an email message via AgentMail | Safe | email |
| `agentmail_list_messages` | List messages in an AgentMail inbox | Safe | email |
| `agentmail_get_message` | Get a specific AgentMail message by ID | Safe | email |
| `agentmail_reply_to_message` | Reply to an existing AgentMail message | Safe | email |
| `agentmail_list_inboxes` | List all AgentMail inboxes | Safe | email |
| `agentmail_create_inbox` | Create a new AgentMail inbox | Safe | email |
| `agentmail_list_threads` | List email threads in an AgentMail inbox | Safe | email |
| `agentmail_create_webhook` | Register a webhook for AgentMail inbox events | Safe | email |

### Gmail Tools (FristonBlanket@gmail.com — direct Gmail API)

Requires: `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` + `GOOGLE_REFRESH_TOKEN`

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `gmail_send_message` | Send email from FristonBlanket@gmail.com | Safe | email |
| `gmail_list_messages` | List inbox messages (supports Gmail query syntax) | Safe | email |
| `gmail_get_message` | Fetch full message content by ID | Safe | email |
| `gmail_create_draft` | Create a Gmail draft (not sent, returns draft ID) | Safe | email |

## Architecture Role

**Extended Layer** — Utility module for agent-initiated communication. Consumed by `logistics/` for notification dispatching.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)

## PAI Dashboard Integration

The email module's functionality is also available via the PAI Dashboard (PMServer.ts, port 8889) as REST endpoints. This provides browser-accessible email without needing the Python MCP bridge.

### MCP Tool → Dashboard Route Mapping

| Python MCP Tool | Dashboard Route | Notes |
|-----------------|-----------------|-------|
| `agentmail_list_inboxes` | `GET /api/email/agentmail/inboxes` | Direct mapping |
| `agentmail_list_messages` | `GET /api/email/agentmail/messages` | Same params |
| `agentmail_get_message` | `GET /api/email/agentmail/message/:id` | Same response shape |
| `agentmail_send_message` | `POST /api/email/agentmail/send` | Same body fields |
| `agentmail_reply_to_message` | `POST /api/email/agentmail/reply/:id` | Same body fields |
| `agentmail_list_threads` | `GET /api/email/agentmail/threads` | Same params |
| `gmail_list_messages` | `GET /api/email/gmail/messages` | Same params |
| `gmail_get_message` | `GET /api/email/gmail/message/:id` | Same response shape |
| `gmail_send_message` | `POST /api/email/gmail/send` | Same body fields |

### OAuth (Dashboard-specific)

Gmail OAuth is managed via dashboard routes not exposed as MCP tools:

- `GET /api/gmail/auth` — initiate OAuth flow (CSRF state generated)
- `GET /api/gmail/callback` — handle callback (CSRF state validated + consumed)
- `GET /api/gmail/status` — check connection status
- `POST /api/gmail/disconnect` — revoke token

Setup guide: `~/.claude/PAI/SYSTEM/EMAIL-SETUP.md`
