"""Custom exceptions for the email module."""

class EmailError(Exception):
    """Base exception for all email-related errors."""
    pass

class EmailAuthError(EmailError):
    """Raised when authentication with the email provider fails."""
    pass

class EmailAPIError(EmailError):
    """Raised when the email provider API returns an error."""
    pass

class MessageNotFoundError(EmailError):
    """Raised when a requested email message is not found."""
    pass

class InvalidMessageError(EmailError):
    """Raised when email data is invalid or missing required fields."""
    pass
