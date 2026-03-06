"""Email module for Codomyrmex.

This module provides generic email interfaces, a Gmail provider, and an AgentMail provider.

Submodules:
    - generics: Provides `EmailMessage`, `EmailDraft`, and abstract `EmailProvider`
    - gmail: Provides `GmailProvider` implementation
    - agentmail: Provides `AgentMailProvider` implementation (API-first agent email)

Installation:
    Install email dependencies with:
    ```bash
    uv sync --extra email
    ```
"""

__version__ = "0.1.0"

from .exceptions import (
    EmailAPIError,
    EmailAuthError,
    EmailError,
    InvalidMessageError,
    MessageNotFoundError,
)
from .generics import EmailAddress, EmailDraft, EmailMessage, EmailProvider

try:
    from .gmail import GMAIL_AVAILABLE, GmailProvider

    EMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    EMAIL_AVAILABLE = False

try:
    from .agentmail import AGENTMAIL_AVAILABLE, AgentMailProvider
except ImportError:
    AGENTMAIL_AVAILABLE = False


def cli_commands():
    """Return CLI commands for the email module."""
    return {
        "status": {
            "help": "Check email module status and dependencies",
            "handler": lambda **kwargs: print(
                f"Email Module v{__version__}\n"
                f"  Available: {EMAIL_AVAILABLE}\n"
                f"  Gmail: {GMAIL_AVAILABLE}\n"
                f"  AgentMail: {AGENTMAIL_AVAILABLE}"
            ),
        }
    }


__all__ = [
    "AGENTMAIL_AVAILABLE",
    # Status flags
    "EMAIL_AVAILABLE",
    "GMAIL_AVAILABLE",
    "AgentMailProvider",
    "EmailAPIError",
    "EmailAddress",
    "EmailAuthError",
    "EmailDraft",
    # Exceptions
    "EmailError",
    "EmailMessage",
    # API endpoints
    "EmailProvider",
    "GmailProvider",
    "InvalidMessageError",
    "MessageNotFoundError",
    # Utilities
    "cli_commands",
]
