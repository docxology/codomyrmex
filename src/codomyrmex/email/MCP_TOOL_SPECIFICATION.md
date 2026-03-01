# Email Module — MCP Tool Specification

This document describes the 12 MCP tools exposed by `codomyrmex.email.mcp_tools`.
AgentMail tools require `AGENTMAIL_API_KEY`. Gmail tools require `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN`.

---

## `agentmail_send_message`

Send an email immediately via AgentMail.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `to` | `List[str]` | Yes | Recipient email addresses |
| `subject` | `str` | Yes | Email subject line |
| `text` | `str` | Yes | Plain-text message body |
| `html` | `str \| None` | No | HTML message body |
| `cc` | `List[str] \| None` | No | CC recipients |
| `bcc` | `List[str] \| None` | No | BCC recipients |
| `inbox_id` | `str \| None` | No | Sending inbox (defaults to `AGENTMAIL_DEFAULT_INBOX`) |

### Output Schema

```json
{
  "status": "ok",
  "message_id": "msg_...",
  "thread_id": "thr_...",
  "subject": "...",
  "to": ["recipient@example.com"]
}
```

---

## `agentmail_list_messages`

List recent messages in an AgentMail inbox.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `inbox_id` | `str \| None` | No | Inbox to query |
| `limit` | `int` | No | Max results (default 20) |
| `labels` | `List[str] \| None` | No | Filter by labels |

### Output Schema

```json
{
  "status": "ok",
  "count": 5,
  "messages": [
    {
      "message_id": "msg_...",
      "thread_id": "thr_...",
      "subject": "...",
      "from": "sender@example.com",
      "date": "2026-02-23T10:00:00",
      "labels": [],
      "preview": "First 200 chars of body..."
    }
  ]
}
```

---

## `agentmail_get_message`

Fetch full content of a specific message.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message_id` | `str` | Yes | AgentMail message ID |
| `inbox_id` | `str \| None` | No | Containing inbox |

### Output Schema

```json
{
  "status": "ok",
  "message": {
    "message_id": "msg_...",
    "thread_id": "thr_...",
    "subject": "...",
    "from": "sender@example.com",
    "from_name": "Sender Name",
    "to": ["recipient@example.com"],
    "cc": [],
    "date": "2026-02-23T10:00:00",
    "body_text": "...",
    "body_html": null,
    "labels": []
  }
}
```

---

## `agentmail_reply_to_message`

Reply to an existing message.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message_id` | `str` | Yes | Message to reply to |
| `text` | `str` | Yes | Plain-text reply body |
| `html` | `str \| None` | No | HTML reply body |
| `reply_all` | `bool` | No | Reply to all recipients (default false) |
| `inbox_id` | `str \| None` | No | Sending inbox |

### Output Schema

```json
{
  "status": "ok",
  "message_id": "msg_...",
  "thread_id": "thr_...",
  "subject": "Re: ..."
}
```

---

## `agentmail_list_inboxes`

List all inboxes for the account.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | `int` | No | Max inboxes to return (default 50) |

### Output Schema

```json
{
  "status": "ok",
  "count": 3,
  "inboxes": [
    {
      "inbox_id": "username@agentmail.to",
      "display_name": "My Inbox",
      "pod_id": null,
      "created_at": "2026-01-01T00:00:00"
    }
  ]
}
```

---

## `agentmail_create_inbox`

Create a new inbox.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | `str \| None` | No | Username (auto-generated if omitted) |
| `display_name` | `str \| None` | No | Human-readable label |

### Output Schema

```json
{
  "status": "ok",
  "inbox_id": "username@agentmail.to",
  "display_name": "My New Inbox",
  "pod_id": null,
  "created_at": "2026-02-23T10:00:00"
}
```

---

## `agentmail_list_threads`

List conversation threads in an inbox.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `inbox_id` | `str \| None` | No | Inbox to query |
| `limit` | `int` | No | Max threads (default 20) |
| `labels` | `List[str] \| None` | No | Filter by labels |

### Output Schema

```json
{
  "status": "ok",
  "count": 4,
  "threads": [
    {
      "thread_id": "thr_...",
      "inbox_id": "username@agentmail.to",
      "subject": "...",
      "message_count": 3,
      "labels": [],
      "created_at": "2026-02-23T09:00:00"
    }
  ]
}
```

---

## `agentmail_create_webhook`

Register a webhook for AgentMail events.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | `str` | Yes | HTTPS endpoint to receive events |
| `event_types` | `List[str]` | Yes | Events to subscribe to (e.g. `["message.received"]`) |
| `inbox_ids` | `List[str] \| None` | No | Scope to specific inboxes |

### Common Event Types

- `message.received` — incoming message arrived
- `message.sent` — outgoing message delivered
- `message.delivered` — delivery confirmed
- `message.bounced` — delivery failed

### Output Schema

```json
{
  "status": "ok",
  "webhook_id": "whk_...",
  "url": "https://example.com/webhook",
  "event_types": ["message.received"],
  "inbox_ids": []
}
```

---

## `gmail_send_message`

Send an email via Gmail API using OAuth2 credentials.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `to` | `List[str]` | Yes | Recipient email addresses |
| `subject` | `str` | Yes | Email subject line |
| `body_text` | `str` | Yes | Plain-text message body |
| `body_html` | `str \| None` | No | HTML message body |
| `cc` | `List[str] \| None` | No | CC recipients |
| `bcc` | `List[str] \| None` | No | BCC recipients |

### Output Schema

```json
{
  "status": "ok",
  "message_id": "msg_...",
  "thread_id": "thr_...",
  "subject": "...",
  "to": ["recipient@example.com"]
}
```

---

## `gmail_list_messages`

List messages in the Gmail inbox with optional search query.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | `str` | No | Gmail search query (e.g. `"is:unread"`, `"from:user@example.com"`). Default: empty (all messages) |
| `max_results` | `int` | No | Maximum messages to return (default 20) |

### Output Schema

```json
{
  "status": "ok",
  "count": 5,
  "messages": [
    {
      "message_id": "msg_...",
      "thread_id": "thr_...",
      "subject": "...",
      "from": "sender@example.com",
      "date": "2026-02-23T10:00:00",
      "labels": [],
      "preview": "First 200 chars of body..."
    }
  ]
}
```

---

## `gmail_get_message`

Fetch a specific Gmail message by its ID.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message_id` | `str` | Yes | The Gmail message ID (opaque string from the Gmail API) |

### Output Schema

```json
{
  "status": "ok",
  "message": {
    "message_id": "msg_...",
    "thread_id": "thr_...",
    "subject": "...",
    "from": "sender@example.com",
    "from_name": "Sender Name",
    "to": ["recipient@example.com"],
    "cc": [],
    "date": "2026-02-23T10:00:00",
    "body_text": "...",
    "body_html": null,
    "labels": []
  }
}
```

---

## `gmail_create_draft`

Create a Gmail draft without sending it.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `to` | `List[str]` | Yes | Recipient email addresses |
| `subject` | `str` | Yes | Email subject line |
| `body_text` | `str` | Yes | Plain-text message body |
| `body_html` | `str \| None` | No | HTML message body |
| `cc` | `List[str] \| None` | No | CC recipients |
| `bcc` | `List[str] \| None` | No | BCC recipients |

### Output Schema

```json
{
  "status": "ok",
  "draft_id": "draft_..."
}
```

---

## Error Response (all tools)

```json
{
  "status": "error",
  "error": "Descriptive error message"
}
```
