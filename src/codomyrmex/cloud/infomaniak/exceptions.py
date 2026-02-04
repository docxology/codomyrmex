"""
Infomaniak Cloud Error Hierarchy.

Provides structured exception types for all Infomaniak cloud operations,
enabling precise error handling and classification.
"""


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
