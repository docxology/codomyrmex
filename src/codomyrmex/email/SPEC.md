# Email Module Specification

## 1. Overview

The `email` module is designed to provide agents with a consistent interface to manage user email. It abstracts away the intricacies of different email providers (Gmail, Outlook, IMAP/SMTP) behind a unified, statically typed interface.

## 2. API Semantics

### 2.1 `EmailMessage`

The `EmailMessage` is a Pydantic `BaseModel` that serves as the universal language for received or sent emails.

**Attributes:**

- `id` (Optional[str]): The unique identifier of the message.
- `thread_id` (Optional[str]): The thread grouping identifier.
- `subject` (str): The subject line of the email.
- `sender` (EmailAddress): An object containing `name` and `email` properties.
- `to`, `cc`, `bcc` (List[EmailAddress]): Lists mapping to their respective headers.
- `body_text` (Optional[str]): Extracted plaintext body.
- `body_html` (Optional[str]): Extracted HTML body.
- `date` (datetime): Extracted transmission date.
- `labels` (List[str]): Provider-specific labels (e.g., 'INBOX', 'UNREAD').

### 2.2 `EmailDraft`

A simplified Pydantic model representing outgoing messages targeting generic provider insertion endpoints. Includes plaintext `body_text` and optional `body_html` counterparts.

### 2.3 `EmailProvider` Protocol

The `EmailProvider` is an `abc.ABC` defining the contract that all specific provider implementations must fulfill.

**Methods:**

- `list_messages(query: str, max_results: int) -> List[EmailMessage]`: Retrieves messages matching a custom search string.
- `get_message(message_id: str) -> EmailMessage`: Retrieves a specific message.
- `send_message(draft: EmailDraft) -> EmailMessage`: Sends a complete outgoing draft directly.
- `create_draft(draft: EmailDraft) -> str`: Inserts the drafted email into the mailbox without sending.
- `delete_message(message_id: str) -> None`: Removes or trashes a message.
- `modify_labels(message_id: str, add_labels: List[str], remove_labels: List[str]) -> None`: Adjusts provider labels.

### 2.4 Exceptions

- `EmailError`: Generic base exception for the module.
- `EmailAuthError`: Represents failures during authentication or authorization.
- `EmailAPIError`: Represents upstream provider failures.
- `MessageNotFoundError`: Raised during retrieval/modification if the ID is missing.
- `InvalidMessageError`: Raised when processing malformed raw payloads.
