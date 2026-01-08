from typing import Optional, Dict, Any

from codomyrmex.logging_monitoring import get_logger





















































logger = get_logger(__name__)
"""
Custom exceptions for Coda.io API errors.

These exceptions map to HTTP status codes returned by the Coda API
and provide structured error handling for API consumers.
"""



class CodaAPIError(Exception):
    """Base exception for all Coda API errors.
    
    Attributes:
        message: Human-readable error message
        status_code: HTTP status code from the API response
        response_body: Raw response body from the API, if available
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
    
    def __str__(self) -> str:
        return f"{self.message} (Status: {self.status_code})"


class CodaForbiddenError(CodaAPIError):
    """Raised when the API token does not grant access to a resource.
    
    HTTP Status Code: 403
    
    This typically occurs when:
    - The token doesn't have permission to access the resource
    - The user is not a member of the workspace
    - The doc has not been shared with the user
    """
    
    def __init__(
        self,
        message: str = "The API token does not grant access to this resource",
        response_body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=403, response_body=response_body)


class CodaNotFoundError(CodaAPIError):
    """Raised when the requested resource could not be found.
    
    HTTP Status Code: 404
    
    This typically occurs when:
    - The doc, page, table, or row ID is invalid
    - The resource has been deleted
    - The resource doesn't exist
    """
    
    def __init__(
        self,
        message: str = "The resource could not be located with the current API token",
        response_body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=404, response_body=response_body)


class CodaGoneError(CodaAPIError):
    """Raised when the requested resource has been deleted.
    
    HTTP Status Code: 410
    
    This typically occurs when:
    - The resource existed but has been permanently deleted
    """
    
    def __init__(
        self,
        message: str = "The resource has been deleted",
        response_body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=410, response_body=response_body)


class CodaRateLimitError(CodaAPIError):
    """Raised when the API rate limit has been exceeded.
    
    HTTP Status Code: 429
    
    Coda API rate limits:
    - Reading data: 100 requests per 6 seconds
    - Writing data: 10 requests per 6 seconds
    - Listing docs: 4 requests per 6 seconds
    
    When this error is raised, you should implement exponential backoff
    and retry the request after waiting.
    """
    
    def __init__(
        self,
        message: str = "The client has sent too many requests",
        response_body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=429, response_body=response_body)


class CodaValidationError(CodaAPIError):
    """Raised when request parameters did not conform to expectations.
    
    HTTP Status Code: 400
    
    This typically occurs when:
    - Required parameters are missing
    - Parameter values are invalid
    - Request body is malformed
    """
    
    def __init__(
        self,
        message: str = "The request parameters did not conform to expectations",
        response_body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=400, response_body=response_body)


class CodaUnprocessableError(CodaAPIError):
    """Raised when the request cannot be processed.
    
    HTTP Status Code: 422
    
    This typically occurs when:
    - The request is syntactically correct but semantically invalid
    - An automation trigger fails validation
    """
    
    def __init__(
        self,
        message: str = "Unable to process the request",
        response_body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=422, response_body=response_body)


def raise_for_status(status_code: int, response_body: Optional[Dict[str, Any]] = None) -> None:
    """Raise the appropriate exception based on HTTP status code.
    
    Args:
        status_code: The HTTP status code from the API response
        response_body: The parsed JSON response body, if available
        
    Raises:
        CodaAuthenticationError: For 401 responses
        CodaForbiddenError: For 403 responses
        CodaNotFoundError: For 404 responses
        CodaGoneError: For 410 responses
        CodaUnprocessableError: For 422 responses
        CodaRateLimitError: For 429 responses
        CodaValidationError: For 400 responses
        CodaAPIError: For other error responses
    """
    if status_code < 400:
        return
    
    # Extract message from response body if available
    message = None
    if response_body:
        message = response_body.get("message") or response_body.get("error")
    
    exception_map = {
        400: CodaValidationError,
        401: CodaAuthenticationError,
        403: CodaForbiddenError,
        404: CodaNotFoundError,
        410: CodaGoneError,
        422: CodaUnprocessableError,
        429: CodaRateLimitError,
    }
    
    exception_class = exception_map.get(status_code, CodaAPIError)
    
    if message:
        raise exception_class(message=message, response_body=response_body)
    elif exception_class == CodaAPIError:
        # Base class requires a message, provide a default
        raise CodaAPIError(
            message=f"API request failed with status code {status_code}",
            status_code=status_code,
            response_body=response_body,
        )
    else:
        raise exception_class(response_body=response_body)
