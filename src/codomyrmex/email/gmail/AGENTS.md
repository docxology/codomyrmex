# Codomyrmex Agents -- src/codomyrmex/email/gmail

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Implements the `EmailProvider` interface for Google Gmail, providing authenticated access to send, list, read, delete, and label-manage email messages via the Gmail REST API. Supports OAuth2 credentials from environment variables, token files, and Application Default Credentials.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `provider.py` | `GmailProvider` | Concrete `EmailProvider` using `google-api-python-client` for all Gmail operations |
| `provider.py` | `GmailProvider.from_env` | Factory classmethod that resolves credentials from env vars, token file, or ADC |
| `provider.py` | `GmailProvider.list_messages` | Lists messages matching a Gmail query string with full metadata fetch |
| `provider.py` | `GmailProvider.get_message` | Fetches a single message by ID with full MIME part parsing |
| `provider.py` | `GmailProvider.send_message` | Sends an email from an `EmailDraft`, returns the sent `EmailMessage` |
| `provider.py` | `GmailProvider.create_draft` | Creates a Gmail draft and returns its draft ID |
| `provider.py` | `GmailProvider.delete_message` | Moves a message to trash |
| `provider.py` | `GmailProvider.modify_labels` | Adds or removes labels on a message |

## Operating Contracts

- Construction raises `ImportError` if `google-api-python-client` / `google-auth` are not installed.
- Construction raises `EmailAuthError` if neither credentials nor a pre-built service object is provided.
- `from_env` tries OAuth2 env vars first, then `~/.codomyrmex/gmail_token.json`, then Application Default Credentials.
- All Gmail API errors are caught as `HttpError` and re-raised as `EmailAPIError` or `MessageNotFoundError` (for 404s).
- MIME parsing handles both single-part and recursive multipart message structures with base64url decoding.
- Tests requiring real API credentials must use `@pytest.mark.skipif` guards -- never mock the Gmail API.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `email.generics` (`EmailProvider`, `EmailAddress`, `EmailDraft`, `EmailMessage`), `email.exceptions`, `google-api-python-client`, `google-auth`
- **Used by**: `email.mcp_tools` (exposes `gmail_send_message`, `gmail_list_messages`, `gmail_get_message`, `gmail_create_draft`)

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
