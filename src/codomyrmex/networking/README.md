# Networking Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Networking module provides HTTP client utilities and WebSocket support for Codomyrmex, enabling API communication and real-time data exchange.

## Key Features

- **HTTP Client**: Full-featured HTTP client with request/response handling
- **WebSocket Client**: Real-time bidirectional communication
- **Response Handling**: Typed response objects with status and content
- **Connection Pooling**: Efficient connection management
- **Timeout Configuration**: Configurable timeouts for requests
- **Retry Logic**: Automatic retry for transient failures

## Quick Start

```python
from codomyrmex.networking import (
    HTTPClient, WebSocketClient, Response,
    get_http_client,
)

# HTTP Client
http = get_http_client()

# GET request
response = http.get("https://api.example.com/users")
if response.status_code == 200:
    users = response.json()

# POST request with JSON body
response = http.post(
    "https://api.example.com/users",
    json={"name": "Alice", "email": "alice@example.com"}
)

# With headers and timeout
response = http.get(
    "https://api.example.com/data",
    headers={"Authorization": "Bearer token"},
    timeout=30
)

# WebSocket Client
ws = WebSocketClient("wss://api.example.com/stream")
ws.connect()
ws.send({"type": "subscribe", "channel": "updates"})

# Receive messages
@ws.on_message
def handle_message(data):
    print(f"Received: {data}")

ws.close()
```

## Core Classes

| Class | Description |
|-------|-------------|
| `HTTPClient` | HTTP request client (GET, POST, PUT, DELETE, etc.) |
| `WebSocketClient` | WebSocket connection with event handling |
| `Response` | HTTP response with status, headers, and content |

## HTTP Methods

| Method | Usage |
|--------|-------|
| `get(url, **kwargs)` | GET request |
| `post(url, json=None, data=None, **kwargs)` | POST request |
| `put(url, json=None, **kwargs)` | PUT request |
| `patch(url, json=None, **kwargs)` | PATCH request |
| `delete(url, **kwargs)` | DELETE request |
| `head(url, **kwargs)` | HEAD request |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `get_http_client()` | Get an HTTP client instance |

## Exceptions

| Exception | Description |
|-----------|-------------|
| `NetworkingError` | Network operations failed |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
