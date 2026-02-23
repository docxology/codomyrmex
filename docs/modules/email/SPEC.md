# Email — Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Email composition, sending, and management through a provider-abstracted interface. Currently supports Gmail with pluggable backend architecture.

## Functional Requirements

### Email Operations

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `EmailDraft(to, subject, body)` | Constructor | Compose outgoing email |
| `provider.send(draft)` | `→ EmailMessage` | Send email via provider |
| `provider.list_messages(query)` | `→ list[EmailMessage]` | Query inbox |

### Provider Interface

| Method | Description |
|--------|-------------|
| `send(draft)` | Send an email draft |
| `list_messages(query)` | List messages matching query |
| `get_message(id)` | Get message by ID |
| `delete_message(id)` | Delete a message |

### Gmail Provider

- **Prerequisite**: `uv sync --extra email` for Gmail dependencies
- **Authentication**: OAuth2 via credentials.json
- **Query syntax**: Gmail search operators (`is:unread`, `from:`, `has:attachment`)
- **Availability**: Check `GMAIL_AVAILABLE` before use

### Exceptions

| Exception | When |
|-----------|------|
| `EmailError` | Base error for all email operations |
| `EmailSendError` | Failed to send email |
| `EmailConnectionError` | Provider connection failure |

## Non-Functional Requirements

- **Provider Independence**: All operations work through abstract `EmailProvider` interface
- **Graceful Degradation**: If Gmail dependencies are not installed, `GMAIL_AVAILABLE` is False

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)
