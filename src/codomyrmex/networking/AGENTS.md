# Codomyrmex Agents — src/codomyrmex/networking

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Networking Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Purpose

Networking module providing HTTP client utilities, WebSocket support, and API client generation for the Codomyrmex platform. This module integrates with `api` and `scrape` modules for network operations.

The networking module serves as the networking layer, providing protocol-agnostic networking interfaces with support for HTTP, WebSocket, and other network protocols.

## Module Overview

### Key Capabilities
- **HTTP Operations**: GET, POST, PUT, DELETE with retries and timeouts
- **WebSocket Communication**: Connect, send, receive, and close WebSocket connections
- **API Client Generation**: Generate API clients from OpenAPI specifications
- **Error Handling**: Network error handling and automatic retries
- **Authentication**: Support for various authentication methods

### Key Features
- Protocol-agnostic networking interface
- Support for HTTP and WebSocket protocols
- Automatic retry and timeout handling
- API client code generation
- Comprehensive error handling

## Function Signatures

### HTTP Client Functions

```python
def get(url: str, **kwargs) -> Response
```

Send a GET request.

**Parameters:**
- `url` (str): Request URL
- `**kwargs`: Additional request options (headers, params, timeout, etc.)

**Returns:** `Response` - HTTP response object

```python
def post(url: str, data: Any, **kwargs) -> Response
```

Send a POST request.

**Parameters:**
- `url` (str): Request URL
- `data` (Any): Request data
- `**kwargs`: Additional request options

**Returns:** `Response` - HTTP response object

```python
def put(url: str, data: Any, **kwargs) -> Response
```

Send a PUT request.

**Parameters:**
- `url` (str): Request URL
- `data` (Any): Request data
- `**kwargs`: Additional request options

**Returns:** `Response` - HTTP response object

```python
def delete(url: str, **kwargs) -> Response
```

Send a DELETE request.

**Parameters:**
- `url` (str): Request URL
- `**kwargs`: Additional request options

**Returns:** `Response` - HTTP response object

```python
def request(method: str, url: str, **kwargs) -> Response
```

Send a custom HTTP request.

**Parameters:**
- `method` (str): HTTP method (GET, POST, etc.)
- `url` (str): Request URL
- `**kwargs`: Additional request options

**Returns:** `Response` - HTTP response object

### WebSocket Client Functions

```python
def connect(url: str) -> bool
```

Connect to a WebSocket server.

**Parameters:**
- `url` (str): WebSocket URL

**Returns:** `bool` - True if connection successful

```python
def send(message: str | bytes) -> bool
```

Send a message over WebSocket.

**Parameters:**
- `message` (str | bytes): Message to send

**Returns:** `bool` - True if send successful

```python
def receive() -> Optional[str | bytes]
```

Receive a message from WebSocket.

**Returns:** `Optional[str | bytes]` - Received message, None if connection closed

```python
def close() -> None
```

Close WebSocket connection.

### API Client Generation Functions

```python
def generate_client(openapi_spec: dict, language: str = "python") -> str
```

Generate API client code from OpenAPI specification.

**Parameters:**
- `openapi_spec` (dict): OpenAPI specification
- `language` (str): Target language (python, javascript, etc.)

**Returns:** `str` - Generated client code

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `http_client.py` – HTTP client implementation
- `websocket_client.py` – WebSocket client implementation
- `api_client_generator.py` – API client code generation

### Documentation
- `README.md` – Module usage and overview
- `AGENTS.md` – This file: agent documentation
- `SPEC.md` – Functional specification

## Operating Contracts

### Universal Networking Protocols

All networking operations within the Codomyrmex platform must:

1. **Error Handling** - Handle network errors gracefully with retries
2. **Timeout Management** - Implement appropriate timeouts
3. **Authentication** - Support various authentication methods
4. **Logging** - Log all network operations for debugging
5. **Resource Cleanup** - Properly close connections and clean up resources

### Integration Guidelines

When integrating with other modules:

1. **Use API Module** - Integrate with API framework for client generation
2. **Scrape Integration** - Support scrape module for HTTP operations
3. **Logging** - Log network operations via logging_monitoring
4. **Error Recovery** - Implement retry logic for transient failures

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Related Modules**:
    - [api](../api/AGENTS.md) - API framework
    - [scrape](../scrape/AGENTS.md) - Web scraping

