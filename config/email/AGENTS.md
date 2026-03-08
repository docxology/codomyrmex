# Email -- Configuration Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the email module. Email integration with Gmail and AgentMail providers.

## Configuration Requirements

Before using email in any PAI workflow, ensure:

1. `AGENTMAIL_API_KEY` is set -- API key for AgentMail service
2. `AGENTMAIL_DEFAULT_INBOX` is set -- Default inbox ID for AgentMail operations
3. `GOOGLE_CLIENT_ID` is set -- Google OAuth client ID for Gmail API
4. `GOOGLE_CLIENT_SECRET` is set -- Google OAuth client secret for Gmail
5. `GOOGLE_REFRESH_TOKEN` is set -- Google OAuth refresh token for Gmail access

## Agent Instructions

1. Verify required environment variables are set before invoking email tools
2. Use `get_config("email.<key>")` from config_management to read module settings
3. Available MCP tools: `agentmail_send_message`, `agentmail_list_messages`, `agentmail_get_message`, `agentmail_reply_to_message`, `agentmail_list_inboxes`, `agentmail_create_inbox`, `agentmail_list_threads`, `agentmail_create_webhook`, `gmail_send_message`, `gmail_list_messages`, `gmail_get_message`, `gmail_create_draft`
4. AgentMail requires an API key. Gmail requires Google OAuth credentials. Install with `uv sync --extra email`.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("email.setting")

# Update configuration
set_config("email.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/email/AGENTS.md)
