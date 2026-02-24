# AgentMail — AI Agent Usage Guidelines

## Overview

This module is purpose-built for AI agents. AgentMail provides API-key-based
authentication that works without interactive OAuth flows — ideal for autonomous
agents operating in production environments.

## Zero-Mock Policy

**Never mock, stub, or fake AgentMail responses in production code.**

- Tests use `@pytest.mark.skipif(not os.getenv("AGENTMAIL_API_KEY"), ...)` to skip gracefully
- No `MagicMock`, `monkeypatch`, `patch`, or `unittest.mock` in test files
- Unimplemented features raise `NotImplementedError`, not silent fallbacks
- Failures are explicit via typed exceptions, never swallowed

## Authentication

```python
# Correct — reads from environment
provider = AgentMailProvider()

# Also correct — explicit key for testing
provider = AgentMailProvider(api_key=os.environ["AGENTMAIL_API_KEY"])

# WRONG — never hardcode credentials
provider = AgentMailProvider(api_key="am_us_hardcoded_key")  # FORBIDDEN
```

## Recommended Usage Patterns

### Inbox-per-Agent Pattern

Each AI agent gets a dedicated inbox for isolation:

```python
inbox = provider.create_inbox(
    username=f"agent-{agent_id}",
    display_name=f"Agent {agent_id} inbox",
)
# Use inbox.inbox_id for all subsequent operations
```

### Webhook for Real-time Events

Register a webhook so the agent receives incoming messages without polling:

```python
webhook = provider.create_webhook(
    url="https://your-agent-server/email-events",
    event_types=["message.received"],
    inbox_ids=[inbox.inbox_id],
)
```

### Pod for Multi-agent Coordination

Group related agent inboxes into a pod:

```python
pod = provider.create_pod(name="research-team")
# Then create inboxes with pod_id=pod.pod_id
```

## Error Handling

Always catch specific exceptions:

```python
from codomyrmex.email.exceptions import (
    EmailAuthError,
    EmailAPIError,
    MessageNotFoundError,
)

try:
    msg = provider.get_message(message_id)
except MessageNotFoundError:
    # Message was already processed or deleted
    pass
except EmailAuthError:
    # API key is invalid or expired
    raise
except EmailAPIError as exc:
    # Rate limiting, server errors, etc.
    logger.error("AgentMail API error: %s", exc)
```

## MCP Tool Usage

The 8 MCP tools are registered under the `"email"` category and are
auto-discovered by the PAI MCP bridge. Use them in agent prompts:

```
Use agentmail_list_messages to check for new emails, then
agentmail_reply_to_message to respond to any that need attention.
```

## Limitations

- Free-text search (`query=` parameter) is not supported by AgentMail — the `query`
  argument in `list_messages` is accepted for interface compatibility but ignored
- Individual message deletion is not available; `delete_message` deletes the
  entire thread containing the specified message
- Attachment binary data requires a separate `get_message_attachment` call
