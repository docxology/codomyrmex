"""
Networking module for Codomyrmex.

This module provides HTTP client utilities, WebSocket support, and API client generation.


Submodules:
    service_mesh: Consolidated service mesh capabilities."""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    pass

# Re-export base NetworkError from main exceptions module
from codomyrmex.exceptions import NetworkError

from . import service_mesh
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
    pass
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
            except (TimeoutError, OSError):
                print(f"  {host}:{port} - UNREACHABLE")

    return {
        "interfaces": {"handler": _interfaces, "help": "List network interfaces"},
        "check": {"handler": _check, "help": "Check network connectivity"},
    }


__all__ = [
    "ConnectionError",
    "DNSResolutionError",
    # Core classes
    "HTTPClient",
    "HTTPError",
    # Exceptions
    "NetworkError",
    "NetworkTimeoutError",
    "PortScanner",
    "ProxyError",
    "RateLimitError",
    "Response",
    "SSHClient",
    "SSHError",
    "SSLError",
    "TCPClient",
    "TCPServer",
    "UDPClient",
    "WebSocketClient",
    "WebSocketError",
    "cli_commands",
    # Functions
    "get_http_client",
    "service_mesh",
]

__version__ = "0.1.0"


def get_http_client() -> HTTPClient:
    """Get an HTTP client instance."""
    return HTTPClient()
