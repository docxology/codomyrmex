# Email Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Email module provides email composition, sending, and management through a provider-abstracted interface. Currently supports Google Mail (Gmail) with a pluggable provider architecture for future backends.

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
| `GmailProvider` | Class | Google Mail implementation |
| `GMAIL_AVAILABLE` | Constant | Whether Gmail dependencies are installed |
| `cli_commands` | Function | CLI commands for email operations |

### Exceptions

| Exception | Purpose |
|-----------|---------|
| `EmailError` | Base email module error |
| `EmailSendError` | Failed to send email |
| `EmailConnectionError` | Provider connection failure |

## Quick Start

```python
from codomyrmex.email import EmailDraft, EmailAddress, EmailProvider

draft = EmailDraft(
    to=[EmailAddress("team@example.com")],
    subject="Sprint Summary",
    body="All tasks completed successfully."
)

provider = EmailProvider()
provider.send(draft)
```

### Gmail Provider

```python
from codomyrmex.email import GmailProvider, GMAIL_AVAILABLE

if GMAIL_AVAILABLE:
    gmail = GmailProvider(credentials_path="~/.gmail/credentials.json")
    messages = gmail.list_messages(query="is:unread")
```

## Architecture

```
email/
├── __init__.py      # All exports
├── generics.py      # EmailAddress, EmailDraft, EmailMessage, EmailProvider
├── exceptions.py    # EmailError, EmailSendError, EmailConnectionError
├── gmail/           # Gmail provider implementation
└── tests/           # Zero-Mock tests (skip if no credentials)
```

## Navigation

- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
