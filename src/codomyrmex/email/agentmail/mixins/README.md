# AgentMail Provider Mixins

> Codomyrmex v1.0.8 | March 2026

## Overview

Focused mixin classes that decompose `AgentMailProvider` into single-responsibility method groups. Each mixin wraps a section of the AgentMail SDK and maps SDK responses to codomyrmex data models (`AgentMailDraft`, `AgentMailInbox`, `AgentMailThread`, `AgentMailWebhook`). All API errors are translated to `EmailAPIError` or `MessageNotFoundError` via a shared `_raise_for_api_error` helper.

## PAI Integration

| PAI Phase | Applicability |
|-----------|---------------|
| EXECUTE   | Compose and send drafts, manage inboxes, register webhooks |
| OBSERVE   | List threads, list inboxes, inspect webhook state |

## Key Exports

| Export          | Source              | Description                                     |
|-----------------|---------------------|-------------------------------------------------|
| `DraftMixin`    | `draft_mixin.py`    | Draft CRUD: create, list, get, update, send, delete |
| `InboxMixin`    | `inbox_mixin.py`    | Inbox CRUD: list, get, create, delete            |
| `ThreadMixin`   | `thread_mixin.py`   | Thread operations: list, get, delete             |
| `WebhookMixin`  | `webhook_mixin.py`  | Webhook CRUD: list, get, create, update, delete  |

## Quick Start

```python
from codomyrmex.email.agentmail.mixins import DraftMixin, InboxMixin

# Mixins are consumed via AgentMailProvider (multiple inheritance):
from codomyrmex.email.agentmail.provider import AgentMailProvider

provider = AgentMailProvider()  # uses AGENTMAIL_API_KEY env var
inboxes = provider.list_inboxes(limit=10)
draft_id = provider.create_draft(draft, inbox_id=inboxes[0].inbox_id)
provider.send_draft(draft_id)
```

## Architecture

```
mixins/
  __init__.py          # Re-exports all four mixin classes
  draft_mixin.py       # DraftMixin  (6 methods, ~200 LOC)
  inbox_mixin.py       # InboxMixin  (4 methods, ~120 LOC)
  thread_mixin.py      # ThreadMixin (3 methods, ~115 LOC)
  webhook_mixin.py     # WebhookMixin (5 methods, ~145 LOC)
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/email/ -k "mixin" -v
```

## Navigation

| Document   | Purpose                     |
|------------|-----------------------------|
| README.md  | This file -- usage guide    |
| AGENTS.md  | Agent coordination rules    |
| SPEC.md    | Technical specification     |
| [Parent](../README.md) | AgentMail provider docs |
