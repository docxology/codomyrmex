# AgentMail Mixins - Agent Coordination

> Codomyrmex v1.1.4 | March 2026

## Overview

Internal mixin classes that compose `AgentMailProvider`. Agents do not interact with mixins directly -- they use the provider's unified interface. This document describes the method contracts agents inherit through the provider.

## Key Files

| File                | Purpose                                      |
|---------------------|----------------------------------------------|
| `__init__.py`       | Re-exports `DraftMixin`, `InboxMixin`, `ThreadMixin`, `WebhookMixin` |
| `draft_mixin.py`    | Draft lifecycle: create, list, get, update, send, delete |
| `inbox_mixin.py`    | Inbox management: list, get, create, delete  |
| `thread_mixin.py`   | Thread operations: list (with label/date filters), get, delete |
| `webhook_mixin.py`  | Webhook CRUD: list, get, create, update, delete |

## MCP Tools Available

No MCP tools are defined in this sub-module. MCP tools for email are defined in the parent `email/mcp_tools.py` and delegate to `AgentMailProvider` which inherits these mixins.

## Agent Instructions

1. Always call methods through `AgentMailProvider`, never instantiate mixins standalone
2. All methods require a valid `AGENTMAIL_API_KEY` environment variable
3. Inbox IDs default to `AGENTMAIL_DEFAULT_INBOX` when not specified -- ensure the env var is set
4. All API errors raise `EmailAPIError` or `MessageNotFoundError` -- handle both
5. Draft `send_draft()` returns `EmailMessage` -- the draft is consumed and no longer exists after sending

## Operating Contracts

- **Error handling**: Every SDK call is wrapped in try/except. `ApiError` from the SDK is translated to codomyrmex exceptions via `_raise_for_api_error`.
- **No silent fallbacks**: Failed API calls always raise. No default/placeholder data is returned.
- **Inbox resolution**: Methods accepting `inbox_id: str | None` resolve `None` to `AGENTMAIL_DEFAULT_INBOX` via `self._resolve_inbox_id()`.
- **Model conversion**: SDK responses are converted to typed dataclasses (`AgentMailDraft`, `AgentMailInbox`, `AgentMailThread`, `AgentMailWebhook`) before return.

## Common Patterns

```python
# Pattern: inbox resolution with fallback to default
resolved_inbox = self._resolve_inbox_id(inbox_id)  # None -> env var default

# Pattern: SDK response extraction
response = self._client.inboxes.drafts.list(resolved_inbox, limit=limit)
items = getattr(response, "drafts", None) or list(response)

# Pattern: error translation
except ApiError as exc:
    _raise_for_api_error(exc, "list_drafts")
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Notes                          |
|------------|-------------|--------------------------------|
| Engineer   | Full        | Extend mixins, add new methods |
| QATester   | Read        | Validate method contracts      |
| Architect  | Read        | Review mixin decomposition     |

## Navigation

| Document   | Purpose                     |
|------------|-----------------------------|
| README.md  | Usage guide                 |
| AGENTS.md  | This file -- agent rules    |
| SPEC.md    | Technical specification     |
| [Parent](../AGENTS.md) | AgentMail agent docs |
