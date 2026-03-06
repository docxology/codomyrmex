"""Network, API, and Validation Exceptions.

Errors related to networking, APIs, validation, and timeouts.
"""

from __future__ import annotations

from typing import Any

from .base import CodomyrmexError


class NetworkError(CodomyrmexError):
    """Raised when network operations fail.

    Attributes:
        message (str): The error message.
        url (str | None): The URL involved in the network operation.
        status_code (int | None): The HTTP status code if available.
    """

    def __init__(
        self,
        message: str,
        url: str | None = None,
        status_code: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if url:
            self.context["url"] = url
        if status_code is not None:
            self.context["status_code"] = status_code


class APIError(CodomyrmexError):
    """Raised when API operations fail.

    Attributes:
        message (str): The error message.
        endpoint (str | None): The API endpoint that failed.
        method (str | None): The HTTP method used.
    """

    def __init__(
        self,
        message: str,
        endpoint: str | None = None,
        method: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if endpoint:
            self.context["endpoint"] = endpoint
        if method:
            self.context["method"] = method


class ValidationError(CodomyrmexError):
    """Raised when data validation fails.

    Attributes:
        message (str): The error message.
        field_name (str | None): Name of the field that failed validation.
        validation_rule (str | None): The rule that was violated.
    """

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        validation_rule: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if field_name:
            self.context["field_name"] = field_name
        if validation_rule:
            self.context["validation_rule"] = validation_rule


class SchemaError(CodomyrmexError):
    """Raised when schema validation fails.

    Attributes:
        message (str): The error message.
        schema_name (str | None): Name of the schema.
        data_preview (str | None): A preview of the data that failed schema validation.
    """

    def __init__(
        self,
        message: str,
        schema_name: str | None = None,
        data_preview: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if schema_name:
            self.context["schema_name"] = schema_name
        if data_preview:
            self.context["data_preview"] = data_preview


class TimeoutError(CodomyrmexError):
    """Raised when operations timeout.

    Attributes:
        message (str): The error message.
        timeout_seconds (float | None): The timeout duration in seconds.
    """

    def __init__(
        self, message: str, timeout_seconds: float | None = None, **kwargs: Any
    ) -> None:
        super().__init__(message, **kwargs)
        if timeout_seconds is not None:
            self.context["timeout_seconds"] = timeout_seconds
