"""
Networking module for Codomyrmex.

This module provides HTTP client utilities, WebSocket support, and API client generation.
"""

from codomyrmex.exceptions import CodomyrmexError

from .http_client import HTTPClient, Response
from .websocket_client import WebSocketClient

__all__ = [
    "HTTPClient",
    "WebSocketClient",
    "Response",
    "get_http_client",
]

__version__ = "0.1.0"


class NetworkingError(CodomyrmexError):
    """Raised when networking operations fail."""

    pass


def get_http_client() -> HTTPClient:
    """Get an HTTP client instance."""
    return HTTPClient()

