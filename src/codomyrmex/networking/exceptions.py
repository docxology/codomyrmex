"""Networking Exception Classes.

This module defines exceptions specific to networking operations including
HTTP requests, WebSocket connections, SSL/TLS, and general network errors.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""

from typing import Any

from codomyrmex.exceptions import NetworkError


class ConnectionError(NetworkError):
    """Raised when a network connection fails.

    Attributes:
        message: Error description.
        host: Target host.
        port: Target port.
        protocol: Connection protocol (TCP, UDP, etc.).
    """

    def __init__(
        self,
        message: str,
        host: str | None = None,
        port: int | None = None,
        protocol: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if host:
            self.context["host"] = host
        if port is not None:
            self.context["port"] = port
        if protocol:
            self.context["protocol"] = protocol


class NetworkTimeoutError(NetworkError):
    """Raised when a network operation times out.

    Attributes:
        message: Error description.
        timeout_seconds: The timeout value that was exceeded.
        operation: The operation that timed out (connect, read, write).
        url: The URL being accessed if applicable.
    """

    def __init__(
        self,
        message: str,
        timeout_seconds: float | None = None,
        operation: str | None = None,
        url: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if timeout_seconds is not None:
            self.context["timeout_seconds"] = timeout_seconds
        if operation:
            self.context["operation"] = operation
        if url:
            self.context["url"] = url


class SSLError(NetworkError):
    """Raised when SSL/TLS operations fail.

    Attributes:
        message: Error description.
        host: Target host.
        certificate_error: Specific certificate error if applicable.
        ssl_version: SSL/TLS version being used.
    """

    def __init__(
        self,
        message: str,
        host: str | None = None,
        certificate_error: str | None = None,
        ssl_version: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if host:
            self.context["host"] = host
        if certificate_error:
            self.context["certificate_error"] = certificate_error
        if ssl_version:
            self.context["ssl_version"] = ssl_version


class HTTPError(NetworkError):
    """Raised when HTTP requests fail.

    Attributes:
        message: Error description.
        status_code: HTTP status code.
        url: The URL that was requested.
        method: HTTP method used (GET, POST, etc.).
        response_body: Truncated response body for debugging.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        url: str | None = None,
        method: str | None = None,
        response_body: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if status_code is not None:
            self.context["status_code"] = status_code
        if url:
            self.context["url"] = url
        if method:
            self.context["method"] = method
        # Truncate response body to avoid huge context
        if response_body:
            self.context["response_body"] = (
                response_body[:500] + "..." if len(response_body) > 500 else response_body
            )


class DNSResolutionError(NetworkError):
    """Raised when DNS resolution fails.

    Attributes:
        message: Error description.
        hostname: The hostname that failed to resolve.
        dns_server: DNS server used if known.
    """

    def __init__(
        self,
        message: str,
        hostname: str | None = None,
        dns_server: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if hostname:
            self.context["hostname"] = hostname
        if dns_server:
            self.context["dns_server"] = dns_server


class WebSocketError(NetworkError):
    """Raised when WebSocket operations fail.

    Attributes:
        message: Error description.
        url: WebSocket URL.
        close_code: WebSocket close code if applicable.
        close_reason: WebSocket close reason if applicable.
    """

    def __init__(
        self,
        message: str,
        url: str | None = None,
        close_code: int | None = None,
        close_reason: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if url:
            self.context["url"] = url
        if close_code is not None:
            self.context["close_code"] = close_code
        if close_reason:
            self.context["close_reason"] = close_reason


class ProxyError(NetworkError):
    """Raised when proxy-related operations fail.

    Attributes:
        message: Error description.
        proxy_url: URL of the proxy server.
        proxy_type: Type of proxy (HTTP, SOCKS5, etc.).
        target_url: The URL being accessed through the proxy.
    """

    def __init__(
        self,
        message: str,
        proxy_url: str | None = None,
        proxy_type: str | None = None,
        target_url: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if proxy_url:
            self.context["proxy_url"] = proxy_url
        if proxy_type:
            self.context["proxy_type"] = proxy_type
        if target_url:
            self.context["target_url"] = target_url


class RateLimitError(NetworkError):
    """Raised when rate limiting is encountered.

    Attributes:
        message: Error description.
        url: The URL that was rate limited.
        retry_after: Time in seconds before retry is allowed.
        limit_type: Type of limit (requests per second, quota, etc.).
    """

    def __init__(
        self,
        message: str,
        url: str | None = None,
        retry_after: float | None = None,
        limit_type: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if url:
            self.context["url"] = url
        if retry_after is not None:
            self.context["retry_after"] = retry_after
        if limit_type:
            self.context["limit_type"] = limit_type


class SSHError(NetworkError):
    """Raised when SSH operations fail.

    Attributes:
        message: Error description.
        host: SSH server host.
        port: SSH server port.
        username: Username used for authentication.
    """

    def __init__(
        self,
        message: str,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if host:
            self.context["host"] = host
        if port is not None:
            self.context["port"] = port
        if username:
            self.context["username"] = username
