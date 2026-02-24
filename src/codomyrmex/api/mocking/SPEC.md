# Technical Specification - Mocking

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.api.mocking`  
**Last Updated**: 2026-01-29

## 1. Purpose

API mock server for development and testing workflows

## 2. Architecture

### 2.1 Components

```
mocking/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `api`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.api.mocking
from codomyrmex.api.mocking import (
    # Enums
    MatchStrategy,         # Enum: EXACT, PREFIX, REGEX
    MockResponseMode,      # Enum: STATIC, SEQUENCE, RANDOM
    # Dataclasses
    MockRequest,           # Request spec: method, path, headers, query_params, body_pattern, match_strategy
    MockResponse,          # Response: status_code, headers, body, latency_ms, error
    MockRoute,             # Binds MockRequest to list of MockResponse with a mode and call_count
    RequestLog,            # Logged request: method, path, headers, body, timestamp, matched_route
    # Classes
    RequestMatcher,        # Evaluates incoming requests against MockRequest specs
    MockAPIServer,         # In-process mock server with route matching, response selection, and assertions
    ResponseFixture,       # Factory for common HTTP responses (success, not_found, server_error, etc.)
    # Factory functions
    create_mock_server,    # Returns new MockAPIServer instance
    create_fixture,        # Returns new ResponseFixture instance
)

# Key class signatures:
class MockAPIServer:
    def add_route(self, name: str, route: MockRoute) -> None: ...
    def remove_route(self, name: str) -> None: ...
    def handle_request(self, method: str, path: str, headers: dict | None = None, body: str | None = None) -> MockResponse: ...
    def get_request_log(self) -> list[RequestLog]: ...
    def clear_log(self) -> None: ...
    def reset(self) -> None: ...
    def assert_called(self, route_name: str, times: int | None = None) -> None: ...
    def assert_not_called(self, route_name: str) -> None: ...

class ResponseFixture:
    @staticmethod
    def success(body: Any = None, headers: dict | None = None) -> MockResponse: ...
    @staticmethod
    def not_found(body: Any = None) -> MockResponse: ...
    @staticmethod
    def server_error(body: Any = None) -> MockResponse: ...
    @staticmethod
    def unauthorized(body: Any = None) -> MockResponse: ...
    @staticmethod
    def rate_limited(retry_after: int = 60) -> MockResponse: ...
    @staticmethod
    def json_response(data: Any, status_code: int = 200) -> MockResponse: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Insertion-order route matching**: Routes are matched in the order they are registered via `add_route`, giving deterministic precedence to earlier routes.
2. **Three response modes**: STATIC (always first), SEQUENCE (round-robin by call count), and RANDOM provide flexible response simulation without external dependencies.
3. **Built-in assertion API**: `assert_called` and `assert_not_called` on `MockAPIServer` allow test verification directly on the server object without separate tracking.

### 4.2 Limitations

- In-process only; does not bind to a real TCP port or handle actual HTTP connections
- `MockRequest` header/query_param matching checks presence but does not yet support pattern matching on header values
- `latency_ms` on `MockResponse` is informational only; `handle_request` does not introduce actual delay

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/api/mocking/
```

## 6. Future Considerations

- Real TCP/HTTP server mode (e.g., wrapping `http.server`) for integration tests that require actual network calls
- Simulated latency injection using `latency_ms` in `handle_request` via `time.sleep` or async delay
- OpenAPI/Swagger spec import to auto-generate mock routes from API definitions
