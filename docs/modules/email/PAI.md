# Personal AI Infrastructure — Email Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Email module provides email composition, sending, and management through a provider-abstracted interface. It supports multiple email protocols and providers with a unified API for drafting, sending, and reading messages.

## PAI Capabilities

### Email Operations

```python
from codomyrmex.email import AgentMailProvider, EmailDraft, AGENTMAIL_AVAILABLE

# Compose and send email
if AGENTMAIL_AVAILABLE:
    draft = EmailDraft(
        to=["team@example.com"],
        subject="Sprint Summary",
        body_text="Completed PAI.md enrichment across 40+ modules."
    )

    provider = AgentMailProvider()
    provider.send_message(draft)
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

## PAI Algorithm Phase Mapping

| Phase | Email Contribution |
|-------|---------------------|
| **EXECUTE** | Send notifications, reports, and alerts |
| **LEARN** | Archive sent/received emails for reference |

## Architecture Role

**Extended Layer** — Utility module for agent-initiated communication. Consumed by `logistics/` for notification dispatching.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
