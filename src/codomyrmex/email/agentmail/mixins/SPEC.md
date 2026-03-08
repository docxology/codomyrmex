# AgentMail Mixins Specification

> Codomyrmex v1.1.9 | March 2026

## Overview

Four mixin classes that decompose `AgentMailProvider` into focused method groups via Python multiple inheritance. Each mixin wraps one domain of the AgentMail REST API through the official `agentmail` Python SDK.

## Design Principles

- **Zero-Mock**: Tests use `@pytest.mark.skipif` when `agentmail` SDK or `AGENTMAIL_API_KEY` is unavailable. No mock objects.
- **Explicit Failure**: All API errors raise `EmailAPIError` or `MessageNotFoundError`. No silent fallbacks or default return values.
- **Single Responsibility**: Each mixin covers exactly one resource domain (drafts, inboxes, threads, webhooks).
- **Uniform Error Translation**: All mixins delegate to a shared `_raise_for_api_error` helper imported from `provider.py`.

## Architecture

```
mixins/
  __init__.py          # Re-exports: DraftMixin, InboxMixin, ThreadMixin, WebhookMixin
  draft_mixin.py       # DraftMixin class
  inbox_mixin.py       # InboxMixin class
  thread_mixin.py      # ThreadMixin class
  webhook_mixin.py     # WebhookMixin class
```

## Functional Requirements

### DraftMixin
- `create_draft(draft: EmailDraft, inbox_id: str | None) -> str` -- create and return draft ID
- `list_drafts(inbox_id: str | None, limit: int) -> list[AgentMailDraft]`
- `get_draft(draft_id: str, inbox_id: str | None) -> AgentMailDraft`
- `update_draft(draft_id, inbox_id, to, cc, bcc, subject, text, html) -> AgentMailDraft`
- `send_draft(draft_id: str, inbox_id: str | None) -> EmailMessage` -- consumes the draft
- `delete_draft(draft_id: str, inbox_id: str | None) -> None`

### InboxMixin
- `list_inboxes(limit: int, page_token: str | None) -> list[AgentMailInbox]`
- `get_inbox(inbox_id: str) -> AgentMailInbox`
- `create_inbox(username, domain, display_name) -> AgentMailInbox`
- `delete_inbox(inbox_id: str) -> None`

### ThreadMixin
- `list_threads(inbox_id, limit, labels, before, after) -> list[AgentMailThread]`
- `get_thread(thread_id: str, inbox_id: str | None) -> AgentMailThread`
- `delete_thread(thread_id: str, inbox_id: str | None) -> None`

### WebhookMixin
- `create_webhook(url: str, event_types: list[str], inbox_ids, pod_ids) -> AgentMailWebhook`
- `list_webhooks(limit: int) -> list[AgentMailWebhook]`
- `get_webhook(webhook_id: str) -> AgentMailWebhook`
- `update_webhook(webhook_id, add_inbox_ids, remove_inbox_ids) -> AgentMailWebhook`
- `delete_webhook(webhook_id: str) -> None`

## Dependencies

| Dependency | Type     | Purpose                        |
|------------|----------|--------------------------------|
| `agentmail` | Optional | Official AgentMail Python SDK |
| `codomyrmex.email.generics` | Internal | `EmailDraft`, `EmailMessage`, `EmailProvider` base types |
| `codomyrmex.email.agentmail.models` | Internal | `AgentMailDraft`, `AgentMailInbox`, `AgentMailThread`, `AgentMailWebhook` dataclasses and SDK-to-model converters |
| `codomyrmex.email.exceptions` | Internal | `EmailAPIError`, `EmailAuthError`, `MessageNotFoundError` |

## Constraints

- All mixins assume `self._client` (AgentMail SDK instance) and `self._resolve_inbox_id()` are provided by the composing `AgentMailProvider` class.
- The `agentmail` SDK import is guarded with try/except -- if not installed, `ApiError` falls back to `Exception`.
- Webhook `create_webhook` requires HTTPS URLs per AgentMail API policy.

## Navigation

| Document   | Purpose                     |
|------------|-----------------------------|
| README.md  | Usage guide                 |
| AGENTS.md  | Agent coordination rules    |
| SPEC.md    | This file -- specification  |
| [Parent](../SPEC.md) | AgentMail specification |
