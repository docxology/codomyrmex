# networking

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

HTTP client utilities, WebSocket support, and API client generation. Provides protocol-agnostic networking interface with retry support, timeout handling, and authentication capabilities for integrating with external services.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `http_client.py` – File
- `websocket_client.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.networking import HTTPClient, WebSocketClient, get_http_client

# HTTP client with retry support
client = HTTPClient(timeout=30, max_retries=3)
response = client.get("https://api.example.com/data")
print(f"Status: {response.status_code}")
print(f"Data: {response.json()}")

# POST request
response = client.post("https://api.example.com/data", data={"key": "value"})

# WebSocket client
ws = WebSocketClient("wss://example.com/ws")
if ws.connect():
    ws.send("Hello, server!")
    message = ws.receive()
    ws.close()
```

