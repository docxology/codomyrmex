# Codomyrmex Agents — src/codomyrmex/networking

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
HTTP client utilities, WebSocket support, and API client generation. Provides protocol-agnostic networking interface with retry support, timeout handling, and authentication capabilities.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `http_client.py` – HTTP client with retry and timeout support
- `websocket_client.py` – WebSocket client for real-time communication

## Key Classes and Functions

### HTTPClient (`http_client.py`)
- `HTTPClient(timeout: int = 30, max_retries: int = 3, retry_backoff: float = 1.0, headers: Optional[dict] = None)` – Initialize HTTP client with retry strategy
- `get(url: str, **kwargs) -> Response` – Send a GET request
- `post(url: str, data: Any = None, **kwargs) -> Response` – Send a POST request
- `put(url: str, data: Any = None, **kwargs) -> Response` – Send a PUT request
- `delete(url: str, **kwargs) -> Response` – Send a DELETE request
- `request(method: str, url: str, **kwargs) -> Response` – Send a custom HTTP request

### Response (`http_client.py`)
- `Response` (dataclass) – HTTP response object:
  - `status_code: int` – HTTP status code
  - `headers: dict` – Response headers
  - `content: bytes` – Response content as bytes
  - `text: str` – Response content as text
  - `json_data: Optional[dict]` – Parsed JSON data (if available)
- `json() -> dict` – Get JSON data from response

### WebSocketClient (`websocket_client.py`)
- `WebSocketClient(url: str)` – Initialize WebSocket client
- `connect() -> bool` – Connect to WebSocket server
- `send(message: Union[str, bytes]) -> bool` – Send a message over WebSocket
- `receive() -> Optional[Union[str, bytes]]` – Receive a message from WebSocket
- `close() -> None` – Close WebSocket connection

### Module Functions (`__init__.py`)
- `get_http_client() -> HTTPClient` – Get an HTTP client instance

### Exceptions
- `NetworkingError` – Raised when networking operations fail

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation