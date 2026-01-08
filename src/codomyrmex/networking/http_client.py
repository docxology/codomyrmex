from typing import Any, Optional
import json
import time

from dataclasses import dataclass
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger




























"""
HTTP client implementation.
"""


try:
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


logger = get_logger(__name__)


class NetworkingError(CodomyrmexError):
    """Raised when networking operations fail."""

    pass


@dataclass
class Response:
    """HTTP response object."""

    status_code: int
    headers: dict
    content: bytes
    text: str
    json_data: Optional[dict] = None

    def json(self) -> dict:
        """Get JSON data from response."""
        if self.json_data is None:
            self.json_data = json.loads(self.text)
        return self.json_data


class HTTPClient:
    """HTTP client with retry and timeout support."""

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
        headers: Optional[dict] = None,
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

    def get(self, url: str, **kwargs) -> Response:
        """Send a GET request.

        Args:
            url: Request URL
            **kwargs: Additional request options

        Returns:
            Response object
        """
        return self.request("GET", url, **kwargs)

    def post(self, url: str, data: Any = None, **kwargs) -> Response:
        """Send a POST request.

        Args:
            url: Request URL
            data: Request data
            **kwargs: Additional request options

        Returns:
            Response object
        """
        return self.request("POST", url, data=data, **kwargs)

    def put(self, url: str, data: Any = None, **kwargs) -> Response:
        """Send a PUT request.

        Args:
            url: Request URL
            data: Request data
            **kwargs: Additional request options

        Returns:
            Response object
        """
        return self.request("PUT", url, data=data, **kwargs)

    def delete(self, url: str, **kwargs) -> Response:
        """Send a DELETE request.

        Args:
            url: Request URL
            **kwargs: Additional request options

        Returns:
            Response object
        """
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
            headers = {**self.default_headers, **kwargs.pop("headers", {})}
            timeout = kwargs.pop("timeout", self.timeout)

            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                **kwargs
            )

            # Parse JSON if possible
            json_data = None
            try:
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

