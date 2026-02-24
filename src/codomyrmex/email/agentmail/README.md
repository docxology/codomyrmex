# AgentMail Email Provider

AgentMail integration for Codomyrmex. Provides comprehensive send/receive capabilities
and AI-agent-native features through the [AgentMail API](https://agentmail.to).

## Why AgentMail

Unlike OAuth-heavy providers, AgentMail uses a simple API key — ideal for automated
AI agents that cannot interactively authorize OAuth flows. It offers:

- **Simple auth** — API key via env var, no browser redirects
- **Inbox management** — create/delete inboxes programmatically
- **Thread organization** — conversation threading out of the box
- **Draft scheduling** — create drafts for later delivery
- **Real-time events** — webhooks and WebSocket for instant notifications
- **Pods** — group inboxes together for multi-agent workflows
- **Domain management** — bring your own domain

## Installation

```bash
uv sync --extra email
```

## Quick Start

```python
import os
from codomyrmex.email import AgentMailProvider
from codomyrmex.email.generics import EmailDraft

provider = AgentMailProvider(
    api_key=os.environ["AGENTMAIL_API_KEY"],
    default_inbox_id="fristonblanket@agentmail.to",
)

# Send an email
draft = EmailDraft(
    subject="Hello from codomyrmex",
    to=["recipient@example.com"],
    body_text="This email was sent by an AI agent.",
)
sent = provider.send_message(draft)
print(f"Sent: {sent.id}")

# List recent messages
messages = provider.list_messages(max_results=10)
for msg in messages:
    print(f"  [{msg.date}] {msg.subject} — from {msg.sender.email}")

# List inboxes
inboxes = provider.list_inboxes()
for inbox in inboxes:
    print(f"  {inbox.inbox_id} ({inbox.display_name})")
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AGENTMAIL_API_KEY` | Yes | AgentMail API key |
| `AGENTMAIL_DEFAULT_INBOX` | No | Default inbox ID for operations |

## API Reference

### EmailProvider Interface

| Method | Description |
|--------|-------------|
| `list_messages(query, max_results, inbox_id, labels, before, after)` | List messages |
| `get_message(message_id, inbox_id)` | Fetch a message by ID |
| `send_message(draft, inbox_id)` | Send immediately |
| `create_draft(draft, inbox_id)` | Create a draft, return draft ID |
| `delete_message(message_id, inbox_id)` | Delete via thread deletion |
| `modify_labels(message_id, add_labels, remove_labels, inbox_id)` | Update labels |

### AgentMail-specific Methods

**Inboxes:** `list_inboxes`, `get_inbox`, `create_inbox`, `delete_inbox`

**Messages (extended):** `reply_to_message`, `forward_message`, `get_message_attachment`, `get_message_raw`

**Threads:** `list_threads`, `get_thread`, `delete_thread`

**Drafts:** `list_drafts`, `get_draft`, `update_draft`, `send_draft`, `delete_draft`

**Webhooks:** `list_webhooks`, `get_webhook`, `create_webhook`, `update_webhook`, `delete_webhook`

**Pods:** `list_pods`, `get_pod`, `create_pod`, `delete_pod`

**Domains:** `list_domains`, `get_domain`

**Metrics:** `get_inbox_metrics`

## MCP Tools

Eight MCP tools are registered for agent consumption:

- `agentmail_send_message` — send email
- `agentmail_list_messages` — list messages
- `agentmail_get_message` — get message by ID
- `agentmail_reply_to_message` — reply to a message
- `agentmail_list_inboxes` — list inboxes
- `agentmail_create_inbox` — create an inbox
- `agentmail_list_threads` — list threads
- `agentmail_create_webhook` — register a webhook

## Zero-Mock Policy

This module follows the project-wide zero-mock policy. Tests use
`@pytest.mark.skipif(not os.getenv("AGENTMAIL_API_KEY"), ...)` guards rather
than mocking the SDK. All production code makes real API calls only.
