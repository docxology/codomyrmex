# Codomyrmex Email Module

The `email` module provides a unified, generic interface for integrating with various email providers, with an initial focus on Google Mail (`gmail`). It adheres strictly to the Codomyrmex Zero-Mock policy, ensuring reliable and verifiable interactions with real email APIs.

## Features

- **Generic Interface:** Define email events and operations using standard Pydantic models and Abstract Base Classes.
- **Google Mail Integration:** Out-of-the-box support for the Gmail API (`v1`).
- **Zero-Mock Testing Compatibility:** Designed to be tested against real APIs using authenticated service accounts or OAuth tokens.

## Installation

Install the module with its optional dependencies:

```bash
uv sync --extra email
```

This will install packages such as `google-api-python-client`, `google-auth-httplib2`, and `google-auth-oauthlib`.

## Quick Start

```python
from codomyrmex.email import GmailProvider, EmailDraft

# Initialize the provider (requires valid credentials)
provider = GmailProvider(credentials=my_google_credentials)

# List messages matching a standard Gmail query string
messages = provider.list_messages(query="is:unread from:boss@example.com", max_results=10)

for msg in messages:
    print(f"Unread message: {msg.subject} from {msg.sender.email}")

# Send a new email
draft = EmailDraft(
    subject="Weekly Update",
    to=["team@example.com"],
    body_text="Here is the status report for this week.",
    body_html="<p>Here is the <strong>status report</strong> for this week.</p>"
)
sent_message = provider.send_message(draft)
print(f"Sent message ID: {sent_message.id}")
```

## Structure

- `exceptions.py`: Custom exceptions for email operations.
- `generics.py`: Standard interfaces (`EmailProvider`, `EmailMessage`, `EmailDraft`, `EmailAddress`).
- `gmail/`: The `GmailProvider` submodule implementation.

For detailed technical specifications, see [SPEC.md](./SPEC.md). For agent instructions on how to use this module, see [AGENTS.md](./AGENTS.md).
