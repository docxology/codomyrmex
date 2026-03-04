"""MCP tool definitions for the networking module.

Exposes network interface listing, connectivity checks, and HTTP client info
as MCP tools for agent consumption.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="networking",
    description="List local network interfaces and their addresses.",
)
def networking_list_interfaces() -> dict[str, Any]:
    """List network interfaces with hostnames and IP addresses.

    Returns:
        dict with keys: status, hostname, addresses
    """
    try:
        import socket

        hostname = socket.gethostname()
        addresses: list[dict[str, str]] = []
        try:
            addrs = socket.getaddrinfo(hostname, None)
            seen: set[str] = set()
            for addr in addrs:
                ip = addr[4][0]
                if ip not in seen:
                    seen.add(ip)
                    addresses.append({"ip": ip, "family": addr[0].name})
        except socket.gaierror:
            pass  # hostname not resolvable — return empty addresses
        return {
            "status": "success",
            "hostname": hostname,
            "addresses": addresses,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="networking",
    description=(
        "Check network connectivity to well-known DNS endpoints. "
        "Returns reachability status for each target."
    ),
)
def networking_check_connectivity(
    timeout: int = 3,
) -> dict[str, Any]:
    """Check basic network connectivity to external DNS services.

    Args:
        timeout: Connection timeout in seconds (default: 3).

    Returns:
        dict with keys: status, results (list of target/reachable pairs)
    """
    try:
        import socket

        targets = [("dns.google", 443), ("1.1.1.1", 53)]
        results: list[dict[str, Any]] = []
        for host, port in targets:
            try:
                sock = socket.create_connection((host, port), timeout=timeout)
                sock.close()
                results.append({"host": host, "port": port, "reachable": True})
            except (TimeoutError, OSError):
                results.append({"host": host, "port": port, "reachable": False})
        return {"status": "success", "results": results}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="networking",
    description="Return the list of HTTP error/exception classes available in the networking module.",
)
def networking_list_exceptions() -> dict[str, Any]:
    """List all networking exception classes and their hierarchy.

    Returns:
        dict with keys: status, exceptions
    """
    try:
        from codomyrmex.networking.exceptions import (
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

        exception_classes = [
            ConnectionError,
            DNSResolutionError,
            HTTPError,
            NetworkTimeoutError,
            ProxyError,
            RateLimitError,
            SSHError,
            SSLError,
            WebSocketError,
        ]
        exceptions = [
            {"name": cls.__name__, "base": cls.__bases__[0].__name__}
            for cls in exception_classes
        ]
        return {"status": "success", "exceptions": exceptions}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
