"""Scraping exceptions hierarchy.

Provides:
- ScrapingError: base error for all scraping operations
- RequestError: HTTP request failures (with status code and URL)
- ParseError: HTML/content parsing failures (with selector context)
- RateLimitError: rate limiting / throttling detection
- CaptchaError: CAPTCHA challenge detection
- AuthenticationError: login/session failures
- ContentNotFoundError: expected content missing from page
- BlockedError: IP/user-agent blocking
"""

from __future__ import annotations

from typing import Any


class ScrapingError(Exception):
    """Base exception for scraping operations."""

    def __init__(
        self,
        message: str = "",
        url: str = "",
        details: dict[str, Any] | None = None,
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.url = url
        self.context = context or {}
        self.details = details or {}
        if self.context:
            self.details.update(self.context)
        super().__init__(message)

    @property
    def error_dict(self) -> dict[str, Any]:
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "url": self.url,
            "details": self.details,
        }


class RequestError(ScrapingError):
    """HTTP request failed."""

    def __init__(
        self,
        message: str = "Request failed",
        url: str = "",
        status_code: int | None = None,
        response_body: str = "",
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body[:500] if response_body else ""
        super().__init__(message, url=url, details={
            "status_code": status_code,
            "response_preview": self.response_body[:200] if self.response_body else "",
        })

    @property
    def is_server_error(self) -> bool:
        return self.status_code is not None and 500 <= self.status_code < 600

    @property
    def is_client_error(self) -> bool:
        return self.status_code is not None and 400 <= self.status_code < 500


class ParseError(ScrapingError):
    """Content parsing failed."""

    def __init__(
        self,
        message: str = "Parse error",
        url: str = "",
        selector: str = "",
        content_preview: str = "",
    ) -> None:
        self.selector = selector
        self.content_preview = content_preview[:200] if content_preview else ""
        super().__init__(message, url=url, details={
            "selector": selector,
            "content_preview": self.content_preview,
        })


class RateLimitError(ScrapingError):
    """Rate limited by the target server."""

    def __init__(
        self,
        message: str = "Rate limited",
        url: str = "",
        retry_after: float | None = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, url=url, details={"retry_after": retry_after})


class CaptchaError(ScrapingError):
    """CAPTCHA challenge detected."""

    def __init__(self, message: str = "CAPTCHA detected", url: str = "", captcha_type: str = "unknown") -> None:
        self.captcha_type = captcha_type
        super().__init__(message, url=url, details={"captcha_type": captcha_type})


class AuthenticationError(ScrapingError):
    """Authentication or session failure."""

    def __init__(self, message: str = "Authentication failed", url: str = "") -> None:
        super().__init__(message, url=url)


class ContentNotFoundError(ScrapingError):
    """Expected content was not found on the page."""

    def __init__(self, message: str = "Content not found", url: str = "", selector: str = "") -> None:
        self.selector = selector
        super().__init__(message, url=url, details={"selector": selector})


class BlockedError(ScrapingError):
    """IP or user-agent has been blocked by the target."""

    def __init__(self, message: str = "Blocked", url: str = "", reason: str = "") -> None:
        self.reason = reason
        super().__init__(message, url=url, details={"reason": reason})


# ── Utility ─────────────────────────────────────────────────────────

def classify_http_error(status_code: int, url: str = "", body: str = "") -> ScrapingError:
    """Create the appropriate exception for an HTTP status code.

    Args:
        status_code: The HTTP response status code.
        url: The request URL.
        body: Optional response body text.

    Returns:
        The most specific ScrapingError subclass.
    """
    if status_code == 429:
        return RateLimitError(url=url)
    if status_code == 401:
        return AuthenticationError(url=url)
    if status_code == 403:
        return BlockedError(url=url, reason=f"HTTP {status_code}")
    if status_code == 404:
        return ContentNotFoundError(url=url)
    return RequestError(
        message=f"HTTP {status_code}",
        url=url,
        status_code=status_code,
        response_body=body,
    )


# ── Aliases (imported by __init__.py) ───────────

# Base class name alias
ScrapeError = ScrapingError


class FirecrawlError(ScrapingError):
    """Error specific to Firecrawl adapter operations."""

    def __init__(
        self,
        message: str = "",
        url: str = "",
        *,
        firecrawl_error: Exception | None = None,
    ) -> None:
        self.firecrawl_error = firecrawl_error
        details: dict[str, Any] = {}
        if firecrawl_error:
            details["firecrawl_error"] = str(firecrawl_error)
        super().__init__(message, url=url, details=details)


class ScrapeConnectionError(RequestError):
    """Connection-level failure during scraping."""


class ScrapeTimeoutError(RequestError):
    """Timeout during a scrape operation."""

    def __init__(self, message: str = "Scrape timed out", url: str = "", timeout: float = 0) -> None:
        self.timeout = timeout
        super().__init__(message, url=url)


class ScrapeValidationError(ScrapingError):
    """Input or output validation failure during scraping."""

    def __init__(
        self,
        message: str = "Validation failed",
        url: str = "",
        *,
        field: str = "",
        value: str = "",
    ) -> None:
        self.field = field
        self.value = value
        details: dict[str, Any] = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value
        super().__init__(message, url=url, details=details)

