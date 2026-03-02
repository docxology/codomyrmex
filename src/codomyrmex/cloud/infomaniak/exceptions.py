"""
Infomaniak Cloud Error Hierarchy.

Provides structured exception types for all Infomaniak cloud operations,
enabling precise error handling and classification.
"""


try:
    import requests as _requests
except ImportError:
    _requests = None  # type: ignore[assignment]


class InfomaniakCloudError(Exception):
    """
    Base exception for all Infomaniak cloud operations.

    Attributes:
        service: The cloud service that raised the error (e.g., "compute", "network")
        operation: The operation that failed (e.g., "create_instance", "list_volumes")
        resource_id: Optional resource identifier involved in the error
    """

    def __init__(
        self,
        message: str,
        service: str = "",
        operation: str = "",
        resource_id: str = "",
    ):
        """Initialize this instance."""
        self.service = service
        self.operation = operation
        self.resource_id = resource_id
        super().__init__(message)


class InfomaniakAuthError(InfomaniakCloudError):
    """Raised when authentication with Infomaniak fails."""
    pass


class InfomaniakNotFoundError(InfomaniakCloudError):
    """Raised when a requested resource is not found (HTTP 404)."""
    pass


class InfomaniakConflictError(InfomaniakCloudError):
    """Raised on state conflicts (HTTP 409), e.g., deleting an in-use resource."""
    pass


class InfomaniakQuotaExceededError(InfomaniakCloudError):
    """Raised when a quota limit is exceeded (HTTP 413)."""
    pass


class InfomaniakConnectionError(InfomaniakCloudError):
    """Raised when a connection to the Infomaniak API fails."""
    pass


class InfomaniakTimeoutError(InfomaniakCloudError):
    """Raised when an operation times out."""
    pass


def classify_openstack_error(
    error: Exception,
    service: str = "",
    operation: str = "",
    resource_id: str = "",
) -> InfomaniakCloudError:
    """
    Classify an OpenStack SDK or HTTP error into the appropriate
    Infomaniak error type.

    Args:
        error: The original exception
        service: Cloud service name for context
        operation: Operation name for context
        resource_id: Resource ID for context

    Returns:
        An appropriate InfomaniakCloudError subclass instance
    """
    error_str = str(error).lower()
    kwargs = dict(service=service, operation=operation, resource_id=resource_id)

    # Check for HTTP status codes in the error message
    if "401" in error_str or "403" in error_str or "authentication" in error_str:
        return InfomaniakAuthError(str(error), **kwargs)
    elif "404" in error_str or "not found" in error_str:
        return InfomaniakNotFoundError(str(error), **kwargs)
    elif "409" in error_str or "conflict" in error_str:
        return InfomaniakConflictError(str(error), **kwargs)
    elif "413" in error_str or "quota" in error_str or "limit" in error_str:
        return InfomaniakQuotaExceededError(str(error), **kwargs)
    elif "timeout" in error_str or "timed out" in error_str:
        return InfomaniakTimeoutError(str(error), **kwargs)
    elif "connection" in error_str or "refused" in error_str or "unreachable" in error_str:
        return InfomaniakConnectionError(str(error), **kwargs)
    else:
        return InfomaniakCloudError(str(error), **kwargs)


def classify_http_error(
    error: Exception,
    service: str = "",
    operation: str = "",
    resource_id: str = "",
) -> InfomaniakCloudError:
    """
    Classify a ``requests`` HTTP error into the appropriate
    Infomaniak error type based on the HTTP status code.

    Works with ``requests.exceptions.HTTPError`` (extracts status code
    from the response), ``requests.exceptions.ConnectionError``,
    ``requests.exceptions.Timeout``, and generic exceptions.

    Args:
        error: The original exception.
        service: Cloud service name for context.
        operation: Operation name for context.
        resource_id: Resource ID for context.

    Returns:
        An appropriate InfomaniakCloudError subclass instance.
    """
    kwargs = dict(service=service, operation=operation, resource_id=resource_id)

    # Connection errors (requires requests)
    if _requests is not None:
        if isinstance(error, _requests.exceptions.ConnectionError):
            return InfomaniakConnectionError(str(error), **kwargs)
        if isinstance(error, _requests.exceptions.Timeout):
            return InfomaniakTimeoutError(str(error), **kwargs)

    # HTTP errors with response status codes
    response = getattr(error, "response", None)
    if response is not None:
        status = getattr(response, "status_code", None)
        if status in (401, 403):
            return InfomaniakAuthError(str(error), **kwargs)
        elif status == 404:
            return InfomaniakNotFoundError(str(error), **kwargs)
        elif status == 409:
            return InfomaniakConflictError(str(error), **kwargs)
        elif status in (413, 429):
            return InfomaniakQuotaExceededError(str(error), **kwargs)

    # Fallback to string-based classification
    return classify_openstack_error(error, **kwargs)
