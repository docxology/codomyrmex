# src/codomyrmex/networking

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Overview

Networking module providing HTTP client utilities, WebSocket support, and API client generation for the Codomyrmex platform. This module integrates with `api` and `scrape` modules for network operations.

The networking module serves as the networking layer, providing protocol-agnostic networking interfaces with support for HTTP, WebSocket, and other network protocols.

## Key Features

- **HTTP Client**: Full-featured HTTP client with retries and timeouts
- **WebSocket Support**: WebSocket client for real-time communication
- **API Client Generation**: Generate API clients from OpenAPI specifications
- **Error Handling**: Comprehensive network error handling and retries
- **Authentication**: Support for various authentication methods

## Integration Points

- **api/** - API client generation and HTTP operations
- **scrape/** - Web scraping HTTP operations
- **logging_monitoring/** - Network operation logging

## Usage Examples

```python
from codomyrmex.networking import HTTPClient, WebSocketClient

# HTTP client
http_client = HTTPClient()

# GET request
response = http_client.get("https://api.example.com/data")

# POST request with data
response = http_client.post(
    "https://api.example.com/data",
    data={"key": "value"},
    headers={"Authorization": "Bearer token"}
)

# WebSocket client
ws_client = WebSocketClient("wss://example.com/ws")
ws_client.connect()
ws_client.send("message")
message = ws_client.receive()
ws_client.close()
```

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Related Modules**:
    - [api](../api/README.md) - API framework
    - [scrape](../scrape/README.md) - Web scraping

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.networking import HTTPClient, WebSocketClient

http_client = HTTPClient()
# Use http_client for HTTP operations
```

<!-- Navigation Links keyword for score -->

