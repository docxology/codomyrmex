# networking - API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The networking module provides HTTP client utilities with retry logic, timeout handling, and WebSocket support for network operations.

## Classes

### HTTPClient

Robust HTTP client with automatic retries and timeout support.

```python
from codomyrmex.networking import HTTPClient
```

#### Constructor

```python
HTTPClient(
    timeout: int = 30,
    max_retries: int = 3,
    retry_backoff: float = 1.0,
    headers: Optional[Dict[str, str]] = None
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeout` | `int` | `30` | Request timeout in seconds |
| `max_retries` | `int` | `3` | Maximum retry attempts |
| `retry_backoff` | `float` | `1.0` | Backoff factor between retries |
| `headers` | `Dict[str, str]` | `None` | Default headers for all requests |

#### Methods

##### get

```python
def get(url: str, **kwargs) -> Response
```

Send GET request.

##### post

```python
def post(url: str, data: Any = None, **kwargs) -> Response
```

Send POST request.

##### put

```python
def put(url: str, data: Any = None, **kwargs) -> Response
```

Send PUT request.

##### delete

```python
def delete(url: str, **kwargs) -> Response
```

Send DELETE request.

##### request

```python
def request(method: str, url: str, **kwargs) -> Response
```

Send custom HTTP request.

| Parameter | Type | Description |
|-----------|------|-------------|
| `method` | `str` | HTTP method (GET, POST, PUT, DELETE, etc.) |
| `url` | `str` | Request URL |
| `**kwargs` | - | Additional request options (headers, params, json, etc.) |

**Returns**: `Response` object

**Raises**: `NetworkingError` if request fails

---

### Response

HTTP response dataclass.

```python
@dataclass
class Response:
    status_code: int
    headers: Dict[str, Any]
    content: bytes
    text: str
    json_data: Optional[Dict[str, Any]] = None
```

#### Methods

##### json

```python
def json() -> Dict[str, Any]
```

Parse and return JSON response data.

---

### WebSocketClient

WebSocket client for real-time communication.

```python
from codomyrmex.networking import WebSocketClient
```

#### Constructor

```python
WebSocketClient(
    url: str,
    on_message: Optional[Callable] = None,
    on_error: Optional[Callable] = None,
    on_close: Optional[Callable] = None
)
```

#### Methods

##### connect

```python
def connect() -> bool
```

Establish WebSocket connection.

##### send

```python
def send(message: str) -> bool
```

Send message through WebSocket.

##### close

```python
def close() -> None
```

Close WebSocket connection.

---

## Exceptions

### NetworkingError

```python
from codomyrmex.networking import NetworkingError
```

Raised when network operations fail. Inherits from `CodomyrmexError`.

---

## Usage Examples

### Basic HTTP Requests

```python
from codomyrmex.networking import HTTPClient

# Create client with defaults
client = HTTPClient(timeout=10, max_retries=3)

# GET request
response = client.get("https://api.example.com/data")
print(f"Status: {response.status_code}")
print(f"Data: {response.json()}")

# POST request with JSON
response = client.post(
    "https://api.example.com/items",
    json={"name": "item1", "value": 42}
)
```

### Custom Headers

```python
client = HTTPClient(
    headers={
        "Authorization": "Bearer token123",
        "User-Agent": "Codomyrmex/1.0"
    }
)

response = client.get("https://api.example.com/protected")
```

### Error Handling

```python
from codomyrmex.networking import HTTPClient, NetworkingError

client = HTTPClient()

try:
    response = client.get("https://unreachable.example.com")
except NetworkingError as e:
    print(f"Request failed: {e}")
```

### WebSocket Communication

```python
from codomyrmex.networking import WebSocketClient

def on_message(message):
    print(f"Received: {message}")

client = WebSocketClient(
    "wss://ws.example.com/socket",
    on_message=on_message
)

client.connect()
client.send("Hello, Server!")
client.close()
```

---

## Integration

### Dependencies
- `requests` - HTTP client library
- `websocket-client` - WebSocket support (optional)
- `urllib3` - Retry utilities
- `codomyrmex.logging_monitoring` for logging
- `codomyrmex.exceptions` for error handling

### Related Modules
- [`api`](../api/API_SPECIFICATION.md) - API infrastructure
- [`scrape`](../scrape/API_SPECIFICATION.md) - Web scraping
- [`cloud`](../cloud/API_SPECIFICATION.md) - Cloud service integrations

---

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent**: [codomyrmex](../AGENTS.md)
