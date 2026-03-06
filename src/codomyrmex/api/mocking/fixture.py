"""ResponseFixture and factory functions for the API mocking module."""

import json
from typing import Any

from .models import MockResponse
from .server import MockAPIServer


class ResponseFixture:
    """Convenience factory with static methods for common HTTP responses."""

    @staticmethod
    def success(
        body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> MockResponse:
        """Return a 200 OK response."""
        return MockResponse(
            status_code=200,
            headers=headers if headers is not None else {},
            body=body,
        )

    @staticmethod
    def not_found(body: Any = None) -> MockResponse:
        """Return a 404 Not Found response."""
        return MockResponse(
            status_code=404,
            body=body if body is not None else {"error": "Not Found"},
        )

    @staticmethod
    def server_error(body: Any = None) -> MockResponse:
        """Return a 500 Internal Server Error response."""
        return MockResponse(
            status_code=500,
            body=body if body is not None else {"error": "Internal Server Error"},
        )

    @staticmethod
    def unauthorized(body: Any = None) -> MockResponse:
        """Return a 401 Unauthorized response."""
        return MockResponse(
            status_code=401,
            body=body if body is not None else {"error": "Unauthorized"},
        )

    @staticmethod
    def rate_limited(retry_after: int = 60) -> MockResponse:
        """Return a 429 Too Many Requests response with a Retry-After header."""
        return MockResponse(
            status_code=429,
            headers={"Retry-After": str(retry_after)},
            body={"error": "Too Many Requests"},
        )

    @staticmethod
    def json_response(data: Any, status_code: int = 200) -> MockResponse:
        """Return a response with a JSON-serialized body and Content-Type header."""
        return MockResponse(
            status_code=status_code,
            headers={"Content-Type": "application/json"},
            body=json.dumps(data),
        )


def create_mock_server() -> MockAPIServer:
    """Create and return a new MockAPIServer instance."""
    return MockAPIServer()


def create_fixture() -> ResponseFixture:
    """Create and return a new ResponseFixture instance."""
    return ResponseFixture()
