"""
Networking module for Codomyrmex.

This module provides HTTP client utilities, WebSocket support, and API client generation.
"""

from .http_client import HTTPClient, Response
from .websocket_client import WebSocketClient
from .ssh_sftp import SSHClient
from .raw_sockets import TCPClient, TCPServer, UDPClient, PortScanner
from .exceptions import (
    ConnectionError,
    NetworkTimeoutError,
    SSLError,
    HTTPError,
    DNSResolutionError,
    WebSocketError,
    ProxyError,
    RateLimitError,
    SSHError,
)

# Re-export base NetworkError from main exceptions module
from codomyrmex.exceptions import NetworkError

__all__ = [
    # Core classes
    "HTTPClient",
    "WebSocketClient",
    "SSHClient",
    "TCPClient",
    "TCPServer",
    "UDPClient",
    "PortScanner",
    "Response",
    # Functions
    "get_http_client",
    # Exceptions
    "NetworkError",
    "ConnectionError",
    "NetworkTimeoutError",
    "SSLError",
    "HTTPError",
    "DNSResolutionError",
    "WebSocketError",
    "ProxyError",
    "RateLimitError",
    "SSHError",
]

__version__ = "0.1.0"


def get_http_client() -> HTTPClient:
    """Get an HTTP client instance."""
    return HTTPClient()


