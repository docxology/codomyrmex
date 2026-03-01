# Email Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `email` module provides a provider-agnostic interface for sending, receiving, and managing email. It ships with two concrete providers: `GmailProvider` (Google Gmail API) and `AgentMailProvider` (AgentMail API). Both implement the abstract `EmailProvider` interface.

Install email dependencies:
```bash
uv sync --extra email
```

## 2. Core Components

### 2.1 Data Models (`generics.py`)

- **`EmailAddress`** (`pydantic.BaseModel`): A single address with `email: str` and optional `name: str`.
- **`EmailMessage`** (`pydantic.BaseModel`): A received/sent message with `id`, `thread_id`, `subject`, `sender` (`EmailAddress`), `to`, `cc`, `bcc` (all `List[EmailAddress]`), `body_text`, `body_html`, `date` (`datetime`), and `labels`.
- **`EmailDraft`** (`pydantic.BaseModel`): An outgoing message draft with `subject`, `to`, `cc`, `bcc` (all `List[str]`), `body_text`, and optional `body_html`.

### 2.2 Abstract Provider (`generics.py`)

**`EmailProvider`** (abstract base class) — all concrete providers implement this interface:

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `list_messages` | `(query="", max_results=100)` | `List[EmailMessage]` | List messages matching a query string |
| `get_message` | `(message_id: str)` | `EmailMessage` | Fetch a specific message by ID |
| `send_message` | `(draft: EmailDraft)` | `EmailMessage` | Send a new email immediately |
| `create_draft` | `(draft: EmailDraft)` | `str` | Create a draft; returns draft ID |
| `delete_message` | `(message_id: str)` | `None` | Delete an email message |
| `modify_labels` | `(message_id, add_labels, remove_labels)` | `None` | Add/remove labels on a message |

### 2.3 Concrete Providers

- **`GmailProvider`**: Implements `EmailProvider` via the Google Gmail API. Auth via `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` + `GOOGLE_REFRESH_TOKEN` env vars (or Application Default Credentials as fallback). Use `GmailProvider.from_env()` to construct from env vars.
- **`AgentMailProvider`**: Implements `EmailProvider` via the AgentMail API. Requires `AGENTMAIL_API_KEY`.

### 2.4 Exception Hierarchy (`exceptions.py`)

```
EmailError (base)
├── EmailAuthError       — authentication with provider failed
├── EmailAPIError        — provider API returned an error
├── MessageNotFoundError — requested message not found
└── InvalidMessageError  — email data invalid or missing required fields
```

### 2.5 Availability Flags

| Flag | Type | Description |
|------|------|-------------|
| `EMAIL_AVAILABLE` | `bool` | True if Gmail dependencies are installed |
| `GMAIL_AVAILABLE` | `bool` | True if Gmail provider is importable |
| `AGENTMAIL_AVAILABLE` | `bool` | True if AgentMail provider is importable |

## 3. Environment Variables

| Variable | Required By | Description |
|----------|-------------|-------------|
| `GOOGLE_CLIENT_ID` | GmailProvider | OAuth2 client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | GmailProvider | OAuth2 client secret from Google Cloud Console |
| `GOOGLE_REFRESH_TOKEN` | GmailProvider | OAuth2 refresh token for FristonBlanket@gmail.com |
| `GOOGLE_APPLICATION_CREDENTIALS` | GmailProvider | Fallback: path to ADC JSON (service account or `gcloud` credentials) |
| `AGENTMAIL_API_KEY` | AgentMailProvider | AgentMail API key |
| `AGENTMAIL_DEFAULT_INBOX` | AgentMailProvider | Default inbox ID for send operations |

## 4. Usage Example

```python
from codomyrmex.email import EmailProvider, EmailDraft, EmailMessage, GMAIL_AVAILABLE

if GMAIL_AVAILABLE:
    from codomyrmex.email import GmailProvider
    provider: EmailProvider = GmailProvider.from_env()

    # List recent messages
    messages = provider.list_messages(query="is:unread", max_results=10)

    # Send an email
    draft = EmailDraft(
        subject="Hello",
        to=["recipient@example.com"],
        body_text="Hello from Codomyrmex!"
    )
    sent = provider.send_message(draft)
    print(f"Sent: {sent.id}")
```
