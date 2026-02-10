"""
Networking module for Codomyrmex.

This module provides HTTP client utilities, WebSocket support, and API client generation.
"""

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# Re-export base NetworkError from main exceptions module
from codomyrmex.exceptions import NetworkError

from .exceptions import (
    ConnectionError,
    DNSResolutionError,
    HTTPError,
    NetworkTimeoutError,
    ProxyError,
    RateLimitError,
    SSHError,
    SSLError,
    WebSocketError,
)
from .http_client import HTTPClient, Response
from .raw_sockets import PortScanner, TCPClient, TCPServer, UDPClient
try:
    from .ssh_sftp import SSHClient
except ImportError:
    SSHClient = None
from .websocket_client import WebSocketClient

def cli_commands():
    """Return CLI commands for the networking module."""
    def _interfaces(**kwargs):
        """List network interfaces."""
        import socket
        hostname = socket.gethostname()
        print("=== Network Interfaces ===")
        print(f"  Hostname: {hostname}")
        try:
            addrs = socket.getaddrinfo(hostname, None)
            seen = set()
            for addr in addrs:
                ip = addr[4][0]
                if ip not in seen:
                    seen.add(ip)
                    print(f"  Address: {ip} ({addr[0].name})")
        except socket.gaierror:
            print("  Could not resolve addresses")

    def _check(**kwargs):
        """Check network connectivity."""
        import socket
        print("=== Connectivity Check ===")
        targets = [("dns.google", 443), ("1.1.1.1", 53)]
        for host, port in targets:
            try:
                sock = socket.create_connection((host, port), timeout=3)
                sock.close()
                print(f"  {host}:{port} - OK")
            except (socket.timeout, OSError):
                print(f"  {host}:{port} - UNREACHABLE")

    return {
        "interfaces": {"handler": _interfaces, "help": "List network interfaces"},
        "check": {"handler": _check, "help": "Check network connectivity"},
    }


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
    "cli_commands",
]

__version__ = "0.1.0"


def get_http_client() -> HTTPClient:
    """Get an HTTP client instance."""
    return HTTPClient()


