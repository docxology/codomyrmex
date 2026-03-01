# Email Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Email module provides email composition, sending, and management through a provider-abstracted interface. Supports **Google Mail (Gmail)** (OAuth2) and **AgentMail** (API-key auth), with a pluggable provider architecture for additional backends.

## Installation

```bash
uv add codomyrmex
# For Gmail support:
uv sync --extra email
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `EmailAddress` | Class | Email address data model |
| `EmailDraft` | Class | Outgoing email composition |
| `EmailMessage` | Class | Complete email message (sent/received) |
| `EmailProvider` | Class | Abstract email provider interface |
| `GmailProvider` | Class | Google Mail implementation (OAuth2) |
| `AgentMailProvider` | Class | AgentMail implementation (API-key) |
| `EMAIL_AVAILABLE` | Constant | Whether any email provider is available |
| `GMAIL_AVAILABLE` | Constant | Whether Gmail dependencies are installed |
| `AGENTMAIL_AVAILABLE` | Constant | Whether AgentMail SDK is installed |
| `cli_commands` | Function | CLI commands for email operations |

### Exceptions

| Exception | Purpose |
|-----------|---------|
| `EmailError` | Base email module error |
| `EmailAuthError` | Authentication failure with provider |
| `EmailAPIError` | Provider API error (quota, 5xx, etc.) |
| `MessageNotFoundError` | Requested message ID not found |
| `InvalidMessageError` | Message data failed validation |

## Quick Start

```python
# AgentMail (requires AGENTMAIL_API_KEY env var)
from codomyrmex.email import AgentMailProvider, EmailDraft, AGENTMAIL_AVAILABLE

if AGENTMAIL_AVAILABLE:
    provider = AgentMailProvider()  # reads AGENTMAIL_API_KEY from environment
    draft = EmailDraft(
        to=["team@example.com"],
        subject="Sprint Summary",
        body_text="All tasks completed successfully."
    )
    sent = provider.send_message(draft)
```

### Gmail Provider

```python
from codomyrmex.email import GmailProvider, GMAIL_AVAILABLE

if GMAIL_AVAILABLE:
    # Reads GOOGLE_REFRESH_TOKEN + GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET from env
    gmail = GmailProvider.from_env()
    messages = gmail.list_messages(query="is:unread")
```

## Architecture

```
email/
├── __init__.py      # All exports, availability flags
├── generics.py      # EmailAddress, EmailDraft, EmailMessage, EmailProvider (ABC)
├── exceptions.py    # EmailError, EmailAuthError, EmailAPIError, MessageNotFoundError, InvalidMessageError
├── mcp_tools.py     # 12 MCP tools (8 AgentMail + 4 Gmail) via @mcp_tool
├── agentmail/       # AgentMail provider (API-key auth)
│   ├── __init__.py
│   ├── models.py    # AgentMail-specific Pydantic models
│   └── provider.py  # AgentMailProvider (35+ methods)
└── gmail/           # Gmail provider (OAuth2)
    ├── __init__.py
    └── provider.py  # GmailProvider (11 methods)
```

## Navigation

- **Extended Docs**: [docs/modules/email/](../../../docs/modules/email/)
- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
