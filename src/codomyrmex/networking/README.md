# networking

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Networking module providing multi-protocol client implementations for HTTP, WebSocket, SSH/SFTP, and raw TCP/UDP socket communication. The `HTTPClient` handles standard HTTP request/response cycles with configurable timeouts and retry logic. `WebSocketClient` supports persistent bidirectional connections. `SSHClient` provides SSH command execution and SFTP file transfers. Raw socket classes (`TCPClient`, `TCPServer`, `UDPClient`) enable low-level network programming, and `PortScanner` discovers open ports on target hosts. Includes a comprehensive exception hierarchy for granular error handling.


## Installation

```bash
uv uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Core Classes

- **`HTTPClient`** -- HTTP client for making GET, POST, PUT, DELETE requests with configurable headers, timeouts, and retries
- **`Response`** -- HTTP response container with status code, headers, and body
- **`WebSocketClient`** -- WebSocket client for persistent bidirectional communication
- **`SSHClient`** -- SSH client for remote command execution and SFTP file transfers
- **`TCPClient`** -- Raw TCP socket client for low-level stream communication
- **`TCPServer`** -- Raw TCP socket server for accepting incoming connections
- **`UDPClient`** -- Raw UDP socket client for datagram communication
- **`PortScanner`** -- Scans target hosts to discover open TCP/UDP ports

### Convenience Functions

- **`get_http_client()`** -- Get an HTTPClient instance with default configuration

### Exceptions

- **`NetworkError`** -- Base exception for all networking errors (from codomyrmex.exceptions)
- **`ConnectionError`** -- Failed to establish a network connection
- **`NetworkTimeoutError`** -- Network operation timed out
- **`SSLError`** -- SSL/TLS handshake or certificate error
- **`HTTPError`** -- HTTP protocol error (4xx/5xx responses)
- **`DNSResolutionError`** -- DNS name could not be resolved
- **`WebSocketError`** -- WebSocket connection or protocol error
- **`ProxyError`** -- Proxy connection or authentication error
- **`RateLimitError`** -- Request rejected due to rate limiting (429)
- **`SSHError`** -- SSH connection, authentication, or command error

## Directory Contents

- `__init__.py` - Module entry point aggregating all protocol clients and exceptions
- `http_client.py` - `HTTPClient` and `Response` for HTTP operations
- `websocket_client.py` - `WebSocketClient` for WebSocket connections
- `ssh_sftp.py` - `SSHClient` for SSH command execution and SFTP transfers
- `raw_sockets.py` - `TCPClient`, `TCPServer`, `UDPClient`, and `PortScanner`
- `exceptions.py` - Full exception hierarchy for networking errors

## Quick Start

```python
from codomyrmex.networking import HTTPClient, WebSocketClient

# Make HTTP requests with retry and timeout support
client = HTTPClient(timeout=10, max_retries=3)
response = client.get("https://api.example.com/users")
print(f"Status: {response.status_code}, Data: {response.json()}")

# POST with JSON data
response = client.post("https://api.example.com/users", data={"name": "Alice"})

# WebSocket for bidirectional communication
ws = WebSocketClient(url="wss://stream.example.com/events")
ws.connect()
ws.send({"subscribe": "ticker"})
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k networking -v
```

## Navigation

- **Full Documentation**: [docs/modules/networking/](../../../docs/modules/networking/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
