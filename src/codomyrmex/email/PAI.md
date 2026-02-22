# Personal AI Infrastructure — Email Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Email module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.email import EmailProvider, EmailMessage, EmailDraft
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `EmailProvider` | Class | Emailprovider |
| `EmailMessage` | Class | Emailmessage |
| `EmailDraft` | Class | Emaildraft |
| `EmailAddress` | Class | Emailaddress |
| `GmailProvider` | Class | Gmailprovider |
| `EMAIL_AVAILABLE` | Class | Email available |
| `GMAIL_AVAILABLE` | Class | Gmail available |
| `EmailError` | Class | Emailerror |
| `EmailAuthError` | Class | Emailautherror |
| `EmailAPIError` | Class | Emailapierror |
| `MessageNotFoundError` | Class | Messagenotfounderror |
| `InvalidMessageError` | Class | Invalidmessageerror |

## PAI Algorithm Phase Mapping

| Phase | Email Contribution |
|-------|------------------------------|
| **EXECUTE** | General module operations |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
