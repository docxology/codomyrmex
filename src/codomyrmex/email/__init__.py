"""Email module for Codomyrmex.

This module provides generic email interfaces and a Gmail provider.

Submodules:
    - generics: Provides `EmailMessage`, `EmailDraft`, and abstract `EmailProvider`
    - gmail: Provides `GmailProvider` implementation

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
    GmailProvider = None  # type: ignore

try:
    from .agentmail import AGENTMAIL_AVAILABLE, AgentMailProvider
except ImportError:
    AGENTMAIL_AVAILABLE = False
    AgentMailProvider = None  # type: ignore

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
    # API endpoints
    "EmailProvider",
    "EmailMessage",
    "EmailDraft",
    "EmailAddress",
    "GmailProvider",
    "AgentMailProvider",
    # Status flags
    "EMAIL_AVAILABLE",
    "GMAIL_AVAILABLE",
    "AGENTMAIL_AVAILABLE",
    # Exceptions
    "EmailError",
    "EmailAuthError",
    "EmailAPIError",
    "MessageNotFoundError",
    "InvalidMessageError",
    # Utilities
    "cli_commands",
]
