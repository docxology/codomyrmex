# Agent Instructions for `codomyrmex.email`

## Context

The `email` module provides the Codomyrmex ecosystem with a unified interface to interact with third-party email providers. It currently features Google Mail (Gmail) support.

## Usage Guidelines

1. **Importing:** Always import `EmailProvider`, `EmailMessage`, `EmailDraft`, and exceptions directly from the `email` module root.

   ```python
   from codomyrmex.email import EmailMessage, EmailError, GmailProvider
   ```

2. **Availability Check:**
   Before running any Gmail code, check the `GMAIL_AVAILABLE` flag, and instruct the user to install the dependencies if it evaluates to `False`.

   ```bash
   uv sync --extra email
   ```

3. **Zero-Mock Policy:**
   When writing tests involving the email module, **never mock** the `GmailProvider` API interactions. Rely strictly on authentic responses. Use `pytest.mark.skipif` to bypass tests if valid credentials are not accessible.

4. **Querying Structure:**
   The `list_messages` method accepts provider-specific syntax via the `query` argument (e.g., `"is:unread"`, `"has:attachment"`, `"from:xyz@abc.com"`). Agents should use valid search modifiers for the currently active backend.
