# Gmail Provider -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements the `EmailProvider` interface for Google Gmail using `google-api-python-client`. Handles OAuth2 credential resolution, MIME message parsing (single-part and recursive multipart), base64url encoding/decoding, and Gmail API error normalization.

## Architecture

`GmailProvider` wraps a `googleapiclient.discovery.Resource` service object. All outbound emails are constructed using Python's `email.message.EmailMessage` and encoded to RFC 2822 raw format. Inbound messages are parsed from Gmail's nested payload structure into the system's `EmailMessage` model.

## Key Classes

### `GmailProvider`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `credentials?, service?` | -- | Initialize with OAuth2 credentials or a pre-built service |
| `from_env` | -- | `GmailProvider` | Factory: resolve credentials from env vars, token file, or ADC |
| `list_messages` | `query?, max_results?, user_id?` | `list[EmailMessage]` | List messages matching Gmail query syntax |
| `get_message` | `message_id, user_id?` | `EmailMessage` | Fetch a single message with full MIME parsing |
| `send_message` | `draft, user_id?` | `EmailMessage` | Send an email and return the sent message |
| `create_draft` | `draft, user_id?` | `str` | Create a draft and return the draft ID |
| `delete_message` | `message_id, user_id?` | `None` | Move a message to trash |
| `modify_labels` | `message_id, add_labels, remove_labels, user_id?` | `None` | Add or remove labels on a message |

### Credential Resolution Order (`from_env`)

1. Explicit OAuth2 env vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`
2. Token file: `~/.codomyrmex/gmail_token.json` (requires `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`)
3. Application Default Credentials: `GOOGLE_APPLICATION_CREDENTIALS`

## Dependencies

- **Internal**: `email.generics` (`EmailProvider`, `EmailAddress`, `EmailDraft`, `EmailMessage`), `email.exceptions`
- **External**: `google-api-python-client`, `google-auth` (optional; guarded by `GMAIL_AVAILABLE` flag)

## Constraints

- Raises `ImportError` at construction if `google-api-python-client` is not installed.
- Raises `EmailAuthError` if neither credentials nor service object is provided.
- Gmail API scopes: `gmail.send`, `gmail.readonly`, `gmail.modify`.
- MIME parsing handles `text/plain` and `text/html` parts recursively.
- Zero-mock: tests requiring real API credentials use `@pytest.mark.skipif` guards.

## Error Handling

- `HttpError` with status 404 raises `MessageNotFoundError`.
- All other `HttpError` responses raise `EmailAPIError`.
- Malformed message payloads raise `InvalidMessageError`.
- All errors logged before propagation.
