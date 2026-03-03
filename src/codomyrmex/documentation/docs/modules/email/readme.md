# Email

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Email module for Codomyrmex.

## Architecture Overview

```
email/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`EmailProvider`**
- **`EmailMessage`**
- **`EmailDraft`**
- **`EmailAddress`**
- **`GmailProvider`**
- **`AgentMailProvider`**
- **`EMAIL_AVAILABLE`**
- **`GMAIL_AVAILABLE`**
- **`AGENTMAIL_AVAILABLE`**
- **`EmailError`**
- **`EmailAuthError`**
- **`EmailAPIError`**
- **`MessageNotFoundError`**
- **`InvalidMessageError`**
- **`cli_commands`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `agentmail_send_message` | Safe |
| `agentmail_list_messages` | Safe |
| `agentmail_get_message` | Safe |
| `agentmail_reply_to_message` | Safe |
| `agentmail_list_inboxes` | Safe |
| `agentmail_create_inbox` | Safe |
| `agentmail_list_threads` | Safe |
| `agentmail_create_webhook` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/email/](../../../../src/codomyrmex/email/)
- **Parent**: [All Modules](../README.md)
