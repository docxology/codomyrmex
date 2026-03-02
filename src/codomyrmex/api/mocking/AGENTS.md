# AI Agent Guidelines — api/mocking

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides an in-process mock API server for testing HTTP integrations without network I/O. Supports route matching, request logging, response fixtures, and assertions against recorded traffic.

## Key Components

| Component | Role |
|-----------|------|
| `MatchStrategy` | Enum: `EXACT`, `PREFIX`, `REGEX` for URL matching |
| `MockResponseMode` | Enum: `STATIC`, `DYNAMIC`, `SEQUENCE` for response generation |
| `MockRequest` / `MockResponse` | Dataclasses representing captured requests and configured responses |
| `MockRoute` | Dataclass binding a path + method + matcher to a response |
| `RequestLog` | Dataclass recording each dispatched request with timestamp |
| `RequestMatcher` | Matches incoming requests against routes using the configured `MatchStrategy` |
| `MockAPIServer` | Central server: route management, request dispatching, request log, assertion methods |
| `ResponseFixture` | Factory producing common responses (200 OK, 404 Not Found, 500 Error, paginated, etc.) |
| `create_mock_server` | Factory returning a configured `MockAPIServer` |
| `create_fixture` | Factory returning a `ResponseFixture` |

## Operating Contracts

- Add routes via `server.add_route(path, method, response)` or fluent builder methods.
- Dispatch via `server.dispatch(request)` which matches routes and returns `MockResponse`.
- All requests are logged in `server.request_log` for post-test assertions.
- `server.assert_called(path, method)` and `server.assert_call_count(path, method, n)` verify expected traffic.
- `ResponseFixture` provides static factory methods for standard HTTP response shapes.
- No network sockets are opened; all dispatch is in-process.

## Integration Points

- **Consumers**: Test suites across the codebase that need HTTP API stubs.
- **Pattern**: Create server via `create_mock_server()`, add routes, pass to code under test.
- **Note**: This is a test utility, not a production mock layer.

## Navigation

- **Parent**: [api/README.md](../README.md)
- **Sibling**: [SPEC.md](SPEC.md) | [README.md](README.md)
- **Root**: [../../../../README.md](../../../../README.md)
