# email -- Agent Capabilities

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `email` module gives agents the ability to send, receive, list, and manage email messages through a provider-abstracted interface. Two provider implementations exist today: **GmailProvider** (Google Mail via OAuth2) and **AgentMailProvider** (AgentMail API-key auth, purpose-built for AI agents). Agents can compose drafts, send messages, read inboxes, manage threads and labels, create inboxes, register webhooks, and forward or reply to messages.

## Active Components

| Component | Type | File | Status |
|-----------|------|------|--------|
| `EmailProvider` | Abstract base class | `generics.py` | Active |
| `EmailMessage` | Pydantic model | `generics.py` | Active |
| `EmailDraft` | Pydantic model | `generics.py` | Active |
| `EmailAddress` | Pydantic model | `generics.py` | Active |
| `GmailProvider` | Concrete provider | `gmail/provider.py` | Active (requires OAuth2 credentials) |
| `AgentMailProvider` | Concrete provider | `agentmail/provider.py` | Active (requires `AGENTMAIL_API_KEY`) |
| `exceptions` | Exception hierarchy | `exceptions.py` | Active |
| `mcp_tools` | MCP tool definitions | `mcp_tools.py` | Active (12 tools: 8 AgentMail + 4 Gmail) |
| `cli_commands` | CLI status handler | `__init__.py` | Active |

## MCP Tools Available

All MCP tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge. AgentMail tools use the AgentMail API (`AGENTMAIL_API_KEY`). Gmail tools use Google OAuth2 (`GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` + `GOOGLE_REFRESH_TOKEN`).

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `agentmail_send_message` | Send an email via AgentMail | Safe |
| `agentmail_list_messages` | List messages in an inbox | Safe |
| `agentmail_get_message` | Fetch a specific message by ID | Safe |
| `agentmail_reply_to_message` | Reply to a specific message | Safe |
| `agentmail_list_inboxes` | List all accessible inboxes | Safe |
| `agentmail_create_inbox` | Create a new inbox | Safe |
| `agentmail_list_threads` | List threads in an inbox | Safe |
| `agentmail_create_webhook` | Register a webhook for events | Safe |
| `gmail_send_message` | Send an email via Gmail API using OAuth2 credentials | Safe |
| `gmail_list_messages` | List messages in the Gmail inbox with optional search query | Safe |
| `gmail_get_message` | Fetch a specific Gmail message by its ID | Safe |
| `gmail_create_draft` | Create a Gmail draft without sending it | Safe |

## Provider Abstract Interface

The `EmailProvider` ABC defines the contract all providers must implement:

| Method | Description |
|--------|-------------|
| `list_messages(query, max_results)` | List messages matching a query |
| `get_message(message_id)` | Fetch a single message by ID |
| `send_message(draft)` | Send an email immediately |
| `create_draft(draft)` | Save a draft and return its ID |
| `delete_message(message_id)` | Delete (trash) a message |
| `modify_labels(message_id, add, remove)` | Add or remove labels |

The `AgentMailProvider` extends this with inbox, thread, draft, webhook, pod, and domain management methods.

## Quick Verification

```bash
# Check module availability
uv run python -c "from codomyrmex.email import EMAIL_AVAILABLE, GMAIL_AVAILABLE, AGENTMAIL_AVAILABLE; print(f'Email: {EMAIL_AVAILABLE}, Gmail: {GMAIL_AVAILABLE}, AgentMail: {AGENTMAIL_AVAILABLE}')"

# Install email dependencies
uv sync --extra email

# Run email tests (requires credentials -- skips gracefully without them)
uv run pytest src/codomyrmex/tests/unit/ -k email -v
uv run pytest src/codomyrmex/tests/integration/email/ -v
```

## Operating Contracts

- **Check availability first.** Always check `GMAIL_AVAILABLE` or `AGENTMAIL_AVAILABLE` before instantiating a provider. If `False`, instruct the user to run `uv sync --extra email`.
- **Authentication requirements.** Gmail requires a `google.oauth2.credentials.Credentials` object or a pre-built `googleapiclient` service. AgentMail requires `AGENTMAIL_API_KEY` set in the environment (optionally `AGENTMAIL_DEFAULT_INBOX`).
- **No credentials in code.** AgentMail reads keys from environment variables exclusively. Gmail accepts credentials objects passed at init time -- never hardcode tokens.
- **Query syntax varies by provider.** Gmail supports Gmail search syntax (`is:unread`, `has:attachment`, `from:xyz@abc.com`). AgentMail does not support free-text search; the `query` parameter is accepted for interface compatibility but ignored.
- **Zero-mock policy.** Tests must never mock provider API calls. Use `@pytest.mark.skipif` to skip tests when valid credentials or SDKs are unavailable.
- **Explicit failures.** All errors raise typed exceptions: `EmailAuthError`, `EmailAPIError`, `MessageNotFoundError`, `InvalidMessageError`. No silent fallbacks.

## Exception Hierarchy

```
EmailError (base)
  +-- EmailAuthError       -- authentication failures
  +-- EmailAPIError        -- provider API errors
  +-- MessageNotFoundError -- requested message/resource not found
  +-- InvalidMessageError  -- malformed or missing message data
```

## Integration Points

| Module | Relationship |
|--------|-------------|
| `calendar_integration` | Shares Google OAuth2 credential flow for Gmail |
| `agents` | Agents invoke MCP email tools for notifications and reports |
| `logistics` | Consumes email module for notification dispatching |
| `events` | Webhook registration enables event-driven email processing |
| `model_context_protocol` | `@mcp_tool` decorators in `mcp_tools.py` enable auto-discovery |

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `agentmail_send_message`, `agentmail_list_messages`, `agentmail_create_inbox`, `gmail_send_message`, `gmail_list_messages`; full inbox management | TRUSTED |
| **Architect** | Read + Design | `agentmail_list_inboxes`, `agentmail_list_messages`; inbox architecture review | OBSERVED |
| **QATester** | Validation | `agentmail_list_messages`, `agentmail_get_message`; message delivery validation | OBSERVED |

### Engineer Agent
**Use Cases**: Agent-to-agent communication via AgentMail, automated email workflows, BUILD phase notifications, Gmail integration for user-facing emails

### Architect Agent
**Use Cases**: Inbox structure review, thread organization design, email routing architecture

### QATester Agent
**Use Cases**: Validate message delivery, verify inbox creation, test webhook registration

## Navigation

- **Module**: `src/codomyrmex/email/`
- **PAI integration**: [PAI.md](PAI.md)
- **Specification**: [SPEC.md](SPEC.md)
- **README**: [README.md](README.md)
- **Parent PAI map**: [../PAI.md](../PAI.md)
