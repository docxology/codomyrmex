# Email — Specification

**Version**: v1.0.1 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Email composition, sending, and management through a provider-abstracted interface. Supports **GmailProvider** (Google Mail via OAuth2) and **AgentMailProvider** (AgentMail API-key auth), with a pluggable provider architecture.

## Functional Requirements

### Email Operations

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `EmailDraft(to, subject, body_text)` | Constructor | Compose outgoing email |
| `provider.send_message(draft)` | `→ EmailMessage` | Send email via provider |
| `provider.list_messages(query)` | `→ list[EmailMessage]` | Query inbox |
| `provider.get_message(id)` | `→ EmailMessage` | Fetch single message |
| `provider.create_draft(draft)` | `→ str` | Save draft, return ID |
| `provider.batch_get_messages(ids)` | `→ list[EmailMessage]` | Fetch multiple messages |

### Provider Interface

| Method | Description |
|--------|-------------|
| `send_message(draft)` | Send an email draft immediately |
| `list_messages(query, max_results)` | List messages matching query |
| `get_message(message_id)` | Get message by ID |
| `create_draft(draft)` | Create a draft without sending |
| `delete_message(message_id)` | Delete (trash) a message |
| `modify_labels(message_id, add, remove)` | Add/remove labels |
| `batch_get_messages(message_ids)` | Fetch multiple messages by ID |

### Gmail Provider

- **Prerequisite**: `uv sync --extra email` for Gmail dependencies
- **Authentication**: `GOOGLE_REFRESH_TOKEN` + `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` env vars; fallback to ADC
- **Constructor**: `GmailProvider.from_env()` (reads credentials from environment)
- **Query syntax**: Gmail search operators (`is:unread`, `from:`, `has:attachment`)
- **Availability**: Check `GMAIL_AVAILABLE` before use
- **Extended methods**: `list_labels`

### AgentMail Provider

- **Authentication**: `AGENTMAIL_API_KEY` env var; optional `AGENTMAIL_DEFAULT_INBOX`
- **Constructor**: `AgentMailProvider()` (reads credentials from environment)
- **Availability**: Check `AGENTMAIL_AVAILABLE` before use
- **Extended methods**: inbox, thread, draft, webhook, pod, domain management, and metrics

### Exceptions

| Exception | When |
|-----------|------|
| `EmailError` | Base error for all email operations |
| `EmailAuthError` | Authentication failure with provider |
| `EmailAPIError` | Provider API error (quota, 5xx, etc.) |
| `MessageNotFoundError` | Requested message ID not found |
| `InvalidMessageError` | Email data failed validation |

## Non-Functional Requirements

- **Provider Independence**: All operations work through abstract `EmailProvider` interface
- **Graceful Degradation**: If Gmail dependencies are not installed, `GMAIL_AVAILABLE` is False
- **Zero-Mock Policy**: All tests must use real functional implementations or authentic fixtures; mocks are forbidden.
- **Comprehensive Logging**: All API operations and errors must be logged.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)
