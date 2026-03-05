"""Custom exceptions for the email module."""


class EmailError(Exception):
    """Base exception for all email-related errors."""


class EmailAuthError(EmailError):
    """Raised when authentication with the email provider fails."""


class EmailAPIError(EmailError):
    """Raised when the email provider API returns an error."""


class MessageNotFoundError(EmailError):
    """Raised when a requested email message is not found."""


class InvalidMessageError(EmailError):
    """Raised when email data is invalid or missing required fields."""
