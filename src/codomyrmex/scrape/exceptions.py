
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger
"""Scrape Module Exception Classes

"""Core functionality module

This module provides exceptions functionality including:
- 4 functions: __init__, __init__, __init__...
- 5 classes: ScrapeError, ScrapeConnectionError, ScrapeTimeoutError...

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
This module defines exception classes specific to the scrape module.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""



class ScrapeError(CodomyrmexError):
    """Base exception class for all scrape-related errors."""

    pass


class ScrapeConnectionError(ScrapeError):
    """Raised when there's a network or connection issue during scraping."""

    def __init__(
    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    url : Description of url
    status_code : Description of status_code

    Returns: Description of return value
"""
        self,
        message: str,
        url: str | None = None,
        status_code: int | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if url:
            self.context["url"] = url
        if status_code:
            self.context["status_code"] = status_code


class ScrapeTimeoutError(ScrapeError):
    """Raised when a scraping operation times out."""

    def __init__(
    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    url : Description of url
    timeout : Description of timeout

    Returns: Description of return value
"""
        self,
        message: str,
        url: str | None = None,
        timeout: float | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if url:
            self.context["url"] = url
        if timeout:
            self.context["timeout"] = timeout


class ScrapeValidationError(ScrapeError):
    """Raised when input validation fails for scraping operations."""

    def __init__(
    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    field : Description of field
    value : Description of value

    Returns: Description of return value
"""
        self,
        message: str,
        field: str | None = None,
        value: str | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if field:
            self.context["field"] = field
        if value:
            self.context["value"] = value


class FirecrawlError(ScrapeError):
    """Raised when Firecrawl-specific errors occur."""

    def __init__(
    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    firecrawl_error : Description of firecrawl_error

    Returns: Description of return value
"""
        self,
        message: str,
        firecrawl_error: Exception | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if firecrawl_error:
            self.context["firecrawl_error_type"] = type(firecrawl_error).__name__
            self.context["firecrawl_error_message"] = str(firecrawl_error)


