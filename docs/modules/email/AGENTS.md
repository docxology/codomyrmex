# Agent Instructions for `codomyrmex.email`

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Context

The `email` module provides the Codomyrmex ecosystem with a unified interface to interact with third-party email providers. It supports two backends: **Gmail** (Google OAuth2) and **AgentMail** (API key-based).

## Usage Guidelines

1. **Importing:** Always import `EmailProvider`, `EmailMessage`, `EmailDraft`, and provider classes directly from the `email` module root.

   ```python
   from codomyrmex.email import EmailMessage, EmailDraft, GmailProvider, AgentMailProvider
   from codomyrmex.email.exceptions import EmailError, EmailAuthError, MessageNotFoundError
   ```

2. **Availability Check:**
   Before running any provider-specific code, check the `EMAIL_AVAILABLE` flag (overall), or `GMAIL_AVAILABLE` / `AGENTMAIL_AVAILABLE` per-provider. Instruct the user to install dependencies if a flag evaluates to `False`.

   ```bash
   uv sync --extra email
   ```

3. **Zero-Mock Policy:**
   When writing tests involving the email module, **never mock** the `GmailProvider` or `AgentMailProvider` API interactions. Rely strictly on authentic responses. Use `pytest.mark.skipif` to bypass tests if valid credentials are not accessible.

4. **Querying Structure:**
   The `list_messages` method accepts provider-specific syntax via the `query` argument (e.g., `"is:unread"`, `"has:attachment"`, `"from:xyz@abc.com"`). Agents should use valid search modifiers for the currently active backend.
