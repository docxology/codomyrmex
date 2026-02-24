from __future__ import annotations
"""
Network, API, and Validation Exceptions

Errors related to networking, APIs, validation, and timeouts.
"""

from typing import Any

from .base import CodomyrmexError


class NetworkError(CodomyrmexError):
    """Raised when network operations fail."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        status_code: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if url:
            self.context["url"] = url
        if status_code is not None:
            self.context["status_code"] = status_code


class APIError(CodomyrmexError):
    """Raised when API operations fail."""
    pass


class ValidationError(CodomyrmexError):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        validation_rule: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if field_name:
            self.context["field_name"] = field_name
        if validation_rule:
            self.context["validation_rule"] = validation_rule


class SchemaError(CodomyrmexError):
    """Raised when schema validation fails."""
    pass


class TimeoutError(CodomyrmexError):
    """Raised when operations timeout."""

    def __init__(
        self, message: str, timeout_seconds: float | None = None, **kwargs: Any
    ) -> None:
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if timeout_seconds is not None:
            self.context["timeout_seconds"] = timeout_seconds
