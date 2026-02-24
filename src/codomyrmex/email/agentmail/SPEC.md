# AgentMail Provider — Technical Specification

## Module Identity

| Field | Value |
|-------|-------|
| Module path | `codomyrmex.email.agentmail` |
| Parent module | `codomyrmex.email` |
| SDK dependency | `agentmail>=0.2.17` |
| Auth mechanism | API key (`AGENTMAIL_API_KEY` env var) |
| Default inbox | `AGENTMAIL_DEFAULT_INBOX` env var |

## Architecture

### Class Hierarchy

```
EmailProvider (abstract, generics.py)
└── AgentMailProvider (provider.py)
```

### Key Files

| File | Role |
|------|------|
| `provider.py` | Main `AgentMailProvider` class (~450 lines) |
| `models.py` | AgentMail-native Pydantic models + SDK conversion helpers |
| `__init__.py` | Package exports: `AgentMailProvider`, `AGENTMAIL_AVAILABLE` |

## SDK Integration

The `AgentMail` client is initialized once in `__init__` and stored as `self._client`.
All SDK calls are wrapped in `try/except ApiError` blocks that convert SDK exceptions
to codomyrmex email exceptions.

### Exception Mapping

| AgentMail status code | Codomyrmex exception |
|-----------------------|---------------------|
| 401, 403 | `EmailAuthError` |
| 404 | `MessageNotFoundError` |
| Any other `ApiError` | `EmailAPIError` |
| Unexpected exceptions | `EmailAPIError` |

### SDK → Generic Model Conversion

`_sdk_message_to_email_message(msg, inbox_id)` in `models.py` converts SDK
`Message` objects to the generic `EmailMessage`. It uses `getattr` for safe
attribute access because the SDK's field names may vary between versions.

Key field mappings:

| SDK field | EmailMessage field |
|-----------|-------------------|
| `message_id` | `id` |
| `thread_id` | `thread_id` |
| `from_` | `sender` (EmailAddress) |
| `to`, `cc`, `bcc` | `to`, `cc`, `bcc` (List[EmailAddress]) |
| `subject` | `subject` |
| `text` | `body_text` |
| `html` | `body_html` |
| `labels` | `labels` |
| `timestamp` / `created_at` | `date` |

## Inbox ID Resolution

Every method that operates on an inbox uses `_resolve_inbox_id(inbox_id)`.
If `inbox_id=None`, it falls back to `self._default_inbox_id`, which is
populated from the `AGENTMAIL_DEFAULT_INBOX` env var on construction.
If neither is set, `EmailAPIError` is raised with a descriptive message.

## `delete_message` Behavior

AgentMail does not support individual message deletion. The `delete_message`
method fetches the message's `thread_id`, then calls
`client.inboxes.threads.delete(inbox_id, thread_id)`. This deletes the entire
thread. For individual-message semantics, use `modify_labels` to apply a
"deleted" or "archived" label instead.

## Available Flag

```python
AGENTMAIL_AVAILABLE: bool  # True iff agentmail SDK is importable
```

This flag is exported from both the submodule and the parent `email` module.
Import guards in `email/__init__.py` prevent `ImportError` when the SDK is absent.

## MCP Tools

All 8 MCP tools in `email/mcp_tools.py` use the `@mcp_tool(category="email")`
decorator and are auto-discovered by the PAI MCP bridge via `pkgutil` scan.

Each tool:
1. Reads `AGENTMAIL_API_KEY` from the environment via `_get_provider()`
2. Delegates to `AgentMailProvider` methods
3. Returns `{"status": "ok", ...}` or `{"status": "error", "error": "..."}`
4. Never accepts credentials as parameters

## Threading Model

All operations are synchronous. The `AgentMail` (not `AsyncAgentMail`) client
is used throughout. For async usage, callers should run methods in a thread
pool executor.
