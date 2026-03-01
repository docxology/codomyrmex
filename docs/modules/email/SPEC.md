# Email — Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Email composition, sending, and management through a provider-abstracted interface. Supports Gmail (Google OAuth2) and AgentMail (API key) with pluggable backend architecture.

## Functional Requirements

### Email Operations

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `EmailDraft(to, subject, body_text)` | Constructor | Compose outgoing email |
| `provider.send_message(draft)` | `→ EmailMessage` | Send email via provider |
| `provider.list_messages(query)` | `→ list[EmailMessage]` | Query inbox |

### Provider Interface

| Method | Description |
|--------|-------------|
| `send_message(draft)` | Send an email draft |
| `list_messages(query)` | List messages matching query |
| `get_message(id)` | Get message by ID |
| `delete_message(id)` | Delete a message |

### Gmail Provider

- **Prerequisite**: `uv sync --extra email` for Gmail dependencies
- **Authentication**: OAuth2 via `GmailProvider.from_env()` using `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` env vars
- **Query syntax**: Gmail search operators (`is:unread`, `from:`, `has:attachment`)
- **Availability**: Check `GMAIL_AVAILABLE` before use

### AgentMail Provider

- **Prerequisite**: `uv sync --extra email` for AgentMail dependencies
- **Authentication**: API key via `AGENTMAIL_API_KEY` env var; constructed as `AgentMailProvider()`
- **Query syntax**: AgentMail inbox/thread filtering
- **Availability**: Check `AGENTMAIL_AVAILABLE` before use

### Exceptions

| Exception | When |
|-----------|------|
| `EmailError` | Base error for all email operations |
| `EmailAuthError` | Authentication failure with provider |
| `EmailAPIError` | Provider API error (quota, 5xx, etc.) |
| `MessageNotFoundError` | Requested message ID not found |
| `InvalidMessageError` | Message data failed validation |

## Non-Functional Requirements

- **Provider Independence**: All operations work through abstract `EmailProvider` interface
- **Graceful Degradation**: If Gmail dependencies are not installed, `GMAIL_AVAILABLE` is False

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)
