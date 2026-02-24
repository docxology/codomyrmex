"""HTTP client implementation.

This module provides a robust HTTP client wrapper with retry logic,
timeouts, and error handling for network operations.
"""

import json
from dataclasses import dataclass
from typing import Any

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    # Mocking for type checking or fallback
    class HTTPAdapter:
        def __init__(self, **kwargs): pass
    class Retry:
        def __init__(self, **kwargs): pass

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class NetworkingError(CodomyrmexError):
    """Raised when networking operations fail."""
    pass


@dataclass
class Response:
    """HTTP response object."""

    status_code: int
    headers: dict[str, Any]
    content: bytes
    text: str
    json_data: dict[str, Any] | None = None

    def json(self) -> dict[str, Any]:
        """Get JSON data from response.

        Returns:
            Parsed JSON data

        Raises:
            NetworkingError: If JSON decoding fails
        """
        if self.json_data is None:
            try:
                self.json_data = json.loads(self.text)
            except json.JSONDecodeError as e:
                raise NetworkingError(f"Failed to decode JSON response: {e}") from e
        return self.json_data


class HTTPClient:
    """HTTP client with retry and timeout support."""

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
        headers: dict[str, str] | None = None,
    ):
        """Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_backoff: Backoff factor for retries
            headers: Default headers
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests package not available. Install with: pip install requests")

        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.default_headers = headers or {}

        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Update session headers
        if self.default_headers:
            self.session.headers.update(self.default_headers)

    def get(self, url: str, **kwargs) -> Response:
        """Send a GET request."""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, data: Any = None, **kwargs) -> Response:
        """Send a POST request."""
        return self.request("POST", url, data=data, **kwargs)

    def put(self, url: str, data: Any = None, **kwargs) -> Response:
        """Send a PUT request."""
        return self.request("PUT", url, data=data, **kwargs)

    def delete(self, url: str, **kwargs) -> Response:
        """Send a DELETE request."""
        return self.request("DELETE", url, **kwargs)

    def request(self, method: str, url: str, **kwargs) -> Response:
        """Send a custom HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request options

        Returns:
            Response object

        Raises:
            NetworkingError: If request fails
        """
        try:
            # Merge headers
            request_headers = {}
            if "headers" in kwargs:
                request_headers = kwargs.pop("headers")

            # Use session options but allow overrides
            timeout = kwargs.pop("timeout", self.timeout)

            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                timeout=timeout,
                **kwargs
            )

            # Parse JSON if possible
            json_data = None
            try:
                if response.content:
                    json_data = response.json()
            except Exception:
                pass

            return Response(
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.content,
                text=response.text,
                json_data=json_data,
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            raise NetworkingError(f"HTTP request failed: {str(e)}") from e
