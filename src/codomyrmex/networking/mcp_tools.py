"""MCP tools for the networking module."""

import json

from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.networking.http_client import HTTPClient
from codomyrmex.networking.raw_sockets import PortScanner


@mcp_tool()
def networking_http_request(
    method: str,
    url: str,
    headers: str | None = None,
    data: str | None = None,
    timeout: int = 30,
) -> str:
    """Make an HTTP request.

    Args:
        method: HTTP method to use (e.g. GET, POST).
        url: The URL to make the request to.
        headers: Optional JSON string of headers to send.
        data: Optional string of data to send in the request body.
        timeout: Timeout in seconds (default 30).

    Returns:
        JSON string containing the status code and response text.
    """
    client = HTTPClient(timeout=timeout)

    parsed_headers = {}
    if headers:
        try:
            parsed_headers = json.loads(headers)
        except json.JSONDecodeError as e:
            return f"Error parsing headers: {e}"

    try:
        response = client.request(
            method=method, url=url, headers=parsed_headers, data=data
        )
        return json.dumps({"status_code": response.status_code, "text": response.text})
    except Exception as e:
        return f"Request failed: {e}"


@mcp_tool()
def networking_port_scan(
    host: str, start_port: int, end_port: int, timeout: float = 0.5
) -> str:
    """Scan a range of ports on a host to see which are open.

    Args:
        host: The host to scan.
        start_port: The starting port number.
        end_port: The ending port number.
        timeout: Timeout per port in seconds.

    Returns:
        JSON string containing the list of open ports.
    """
    try:
        open_ports = PortScanner.scan_range(host, start_port, end_port, timeout=timeout)
        return json.dumps({"open_ports": open_ports})
    except Exception as e:
        return f"Scan failed: {e}"
