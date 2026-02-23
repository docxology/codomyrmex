# Mocking

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

API mock server for development and testing workflows.

## Overview

The `mocking` submodule provides a configurable mock API server with route matching (exact, prefix, regex), multiple response modes (static, sequence, random), request logging, and assertion helpers.

## Quick Start

```python
from codomyrmex.api.mocking import (
    MockRequest, MockResponse, MockRoute, MatchStrategy, MockResponseMode,
    create_mock_server, create_fixture,
)

# Create a mock server
server = create_mock_server()
fixture = create_fixture()

# Add routes
server.add_route("get-users", MockRoute(
    request=MockRequest(method="GET", path="/api/users"),
    responses=[fixture.success(body={"users": []})],
))

server.add_route("api-prefix", MockRoute(
    request=MockRequest(method="GET", path="/api/", match_strategy=MatchStrategy.PREFIX),
    responses=[fixture.json_response({"status": "ok"})],
))

server.add_route("user-by-id", MockRoute(
    request=MockRequest(method="GET", path=r"/users/\d+", match_strategy=MatchStrategy.REGEX),
    responses=[
        MockResponse(status_code=200, body={"id": 1}),
        MockResponse(status_code=200, body={"id": 2}),
    ],
    mode=MockResponseMode.SEQUENCE,
))

# Handle requests
response = server.handle_request("GET", "/api/users")
assert response.status_code == 200

# Assertions
server.assert_called("get-users", times=1)
server.assert_not_called("api-prefix")

# Request logging
log = server.get_request_log()

# Common response fixtures
fixture.success(body={"ok": True})    # 200
fixture.not_found()                    # 404
fixture.server_error()                 # 500
fixture.unauthorized()                 # 401
fixture.rate_limited(retry_after=60)   # 429
fixture.json_response({"key": "val"})  # 200 + Content-Type: application/json
```

## Features

- Route matching: exact path, prefix, and regex strategies
- Response modes: static, round-robin sequence, and random
- Request logging with matched route tracking
- Assertion helpers for verifying call counts
- Built-in response fixtures for common HTTP status codes
- Body pattern matching with regex

## API Reference

See [API_SPECIFICATION.md](./API_SPECIFICATION.md) for detailed API documentation.

## Related Modules

- [`api`](../) - Parent module
- [`api.webhooks`](../webhooks/) - Webhook testing use case
