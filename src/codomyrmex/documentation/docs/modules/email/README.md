<!-- readme: generated -->

# email

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/email/`

## Overview

Email module for Codomyrmex.

This module provides generic email interfaces, a Gmail provider, and an AgentMail provider.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `generics:` | Provides `EmailMessage`, `EmailDraft`, and abstract `EmailProvider` |
| `gmail:` | Provides `GmailProvider` implementation |
| `agentmail:` | Provides `AgentMailProvider` implementation (API-first agent email) |

## Public Exports

`email` exports 15 public symbols via `__all__`:

`AGENTMAIL_AVAILABLE`, `EMAIL_AVAILABLE`, `GMAIL_AVAILABLE`, `AgentMailProvider`, `EmailAPIError`, `EmailAddress`, `EmailAuthError`, `EmailDraft`, `EmailError`, `EmailMessage`, `EmailProvider`, `GmailProvider`, `InvalidMessageError`, `MessageNotFoundError`, `cli_commands`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../email/](../../../../email/)
