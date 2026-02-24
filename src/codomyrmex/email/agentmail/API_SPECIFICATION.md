# AgentMail Submodule — API Specification

**Module**: `codomyrmex.email.agentmail`
**Version**: v1.0.0
**Provider**: AgentMail (https://agentmail.to)

## Overview

The `agentmail` submodule implements the `EmailProvider` interface backed by the
AgentMail API. It provides full send/receive capabilities plus AgentMail-specific
features: inbox management, threads, drafts, webhooks, pods, and domains.

**Authentication**: Exclusively via `AGENTMAIL_API_KEY` environment variable.
No credentials are stored in code.

**Installation**: `uv sync --extra email`

---

## Availability Check

```python
from codomyrmex.email.agentmail import AGENTMAIL_AVAILABLE

if AGENTMAIL_AVAILABLE:
    # SDK installed and ready
    ...
```

`AGENTMAIL_AVAILABLE: bool` — `True` when the `agentmail` SDK is installed.

---

## `AgentMailProvider`

### Constructor

```python
AgentMailProvider(
    api_key: str | None = None,
    default_inbox_id: str | None = None,
) -> None
```

**Parameters:**
- `api_key` — AgentMail API key. Defaults to `AGENTMAIL_API_KEY` env var.
- `default_inbox_id` — Default inbox for operations when not specified. Defaults to `AGENTMAIL_DEFAULT_INBOX` env var.

**Raises:**
- `ImportError` — If the `agentmail` SDK is not installed.
- `EmailAuthError` — If no API key is available from argument or env var.

---

## EmailProvider Interface Methods

### `list_messages`

```python
list_messages(
    query: str = "",
    max_results: int = 100,
    inbox_id: str | None = None,
    labels: list[str] | None = None,
    before: str | None = None,
    after: str | None = None,
) -> list[EmailMessage]
```

List messages in an inbox. Note: `query` is accepted for interface compatibility
but **ignored** — AgentMail does not support free-text search.

### `get_message`

```python
get_message(
    message_id: str,
    inbox_id: str | None = None,
) -> EmailMessage
```

Fetch a specific message by ID.

**Raises:** `MessageNotFoundError` if the message does not exist.

### `send_message`

```python
send_message(
    draft: EmailDraft,
    inbox_id: str | None = None,
) -> EmailMessage
```

Send an email immediately. Returns the sent `EmailMessage`.

### `create_draft`

```python
create_draft(
    draft: EmailDraft,
    inbox_id: str | None = None,
) -> str
```

Create a draft. Returns the draft ID string.

### `delete_message`

```python
delete_message(
    message_id: str,
    inbox_id: str | None = None,
) -> None
```

Delete a message. **Note**: AgentMail does not support individual message deletion —
this method deletes the entire thread containing the message.

### `modify_labels`

```python
modify_labels(
    message_id: str,
    add_labels: list[str],
    remove_labels: list[str],
    inbox_id: str | None = None,
) -> None
```

Add or remove labels from a message.

---

## AgentMail-Specific Methods

### Inbox Management

```python
list_inboxes(limit: int = 100) -> list[AgentMailInbox]
create_inbox(
    username: str | None = None,
    display_name: str | None = None,
) -> AgentMailInbox
get_inbox(inbox_id: str) -> AgentMailInbox
delete_inbox(inbox_id: str) -> None
```

### Draft Management

```python
get_draft(draft_id: str, inbox_id: str | None = None) -> AgentMailDraft
list_drafts(limit: int = 100, inbox_id: str | None = None) -> list[AgentMailDraft]
send_draft(draft_id: str, inbox_id: str | None = None) -> EmailMessage
delete_draft(draft_id: str, inbox_id: str | None = None) -> None
```

### Thread Management

```python
list_threads(
    limit: int = 100,
    inbox_id: str | None = None,
) -> list[AgentMailThread]
get_thread(thread_id: str, inbox_id: str | None = None) -> AgentMailThread
delete_thread(thread_id: str, inbox_id: str | None = None) -> None
```

### Reply

```python
reply_to_message(
    message_id: str,
    text: str | None = None,
    html: str | None = None,
    inbox_id: str | None = None,
) -> EmailMessage
```

### Webhook Management

```python
create_webhook(
    url: str,
    event_types: list[str] | None = None,
) -> AgentMailWebhook
get_webhook(webhook_id: str) -> AgentMailWebhook
list_webhooks() -> list[AgentMailWebhook]
delete_webhook(webhook_id: str) -> None
```

### Pod Management

```python
create_pod(name: str | None = None) -> AgentMailPod
get_pod(pod_id: str) -> AgentMailPod
list_pods() -> list[AgentMailPod]
delete_pod(pod_id: str) -> None
```

### Domain Management

```python
register_domain(domain: str) -> AgentMailDomain
get_domain(domain: str) -> AgentMailDomain
list_domains() -> list[AgentMailDomain]
delete_domain(domain: str) -> None
```

---

## Data Models

All models are defined in `codomyrmex.email.agentmail.models`.

| Model | Key Fields |
|-------|-----------|
| `AgentMailInbox` | `inbox_id`, `address`, `display_name` |
| `AgentMailDraft` | `draft_id`, `inbox_id`, `subject`, `to`, `text`, `html` |
| `AgentMailThread` | `thread_id`, `inbox_id`, `subject`, `message_count` |
| `AgentMailWebhook` | `webhook_id`, `url`, `event_types`, `created_at` |
| `AgentMailPod` | `pod_id`, `name`, `inbox_ids`, `created_at` |
| `AgentMailDomain` | `domain`, `status`, `created_at` |

---

## Exceptions

All exceptions are from `codomyrmex.email.exceptions`:

| Exception | When Raised |
|-----------|-------------|
| `EmailAuthError` | Missing or invalid API key (HTTP 401/403) |
| `MessageNotFoundError` | Resource does not exist (HTTP 404) |
| `EmailAPIError` | All other API errors |
| `ImportError` | `agentmail` SDK not installed |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AGENTMAIL_API_KEY` | Yes | — | AgentMail API key (`am_us_...`) |
| `AGENTMAIL_DEFAULT_INBOX` | No | — | Default inbox ID for operations |
