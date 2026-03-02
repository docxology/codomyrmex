"""
Mocking Submodule

API mock server for development and testing workflows.

Provides configurable mock routes with request matching strategies,
multiple response modes (static, sequence, round-robin, random),
and request logging for assertion-based testing.
"""

__version__ = "0.1.0"

import json
import random as _random
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MatchStrategy(Enum):
    """Strategy used to match an incoming request path against a mock route."""

    EXACT = "exact"
    PREFIX = "prefix"
    REGEX = "regex"

class MockResponseMode(Enum):
    """Determines how a mock route selects which response to return."""

    STATIC = "static"
    SEQUENCE = "sequence"
    RANDOM = "random"

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class MockRequest:
    """
    Specification for matching incoming requests.

    Fields:
        method: HTTP method to match (case-insensitive comparison).
        path: Path pattern interpreted according to *match_strategy*.
        headers: Headers that must be present (subset match).
        query_params: Query parameters that must be present (subset match).
        body_pattern: Optional regex pattern applied to the request body.
        match_strategy: How *path* is compared to the incoming request path.
    """

    method: str = "GET"
    path: str = "/"
    headers: dict[str, str] = field(default_factory=dict)
    query_params: dict[str, str] = field(default_factory=dict)
    body_pattern: str | None = None
    match_strategy: MatchStrategy = MatchStrategy.EXACT

@dataclass
class MockResponse:
    """
    A canned response returned by the mock server.

    Fields:
        status_code: HTTP status code.
        headers: Response headers.
        body: Arbitrary response body (string, dict, bytes, etc.).
        latency_ms: Simulated latency in milliseconds (informational).
        error: Optional error message indicating a simulated failure.
    """

    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    body: Any = None
    latency_ms: float = 0.0
    error: str | None = None

@dataclass
class MockRoute:
    """
    Binds a request specification to one or more possible responses.

    Fields:
        request: The request specification to match against.
        responses: Ordered list of responses available for this route.
        mode: How a response is selected from *responses*.
        call_count: Number of times this route has been matched.
    """

    request: MockRequest = field(default_factory=MockRequest)
    responses: list[MockResponse] = field(default_factory=list)
    mode: MockResponseMode = MockResponseMode.STATIC
    call_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize the route to a plain dictionary."""
        return {
            "request": {
                "method": self.request.method,
                "path": self.request.path,
                "headers": dict(self.request.headers),
                "query_params": dict(self.request.query_params),
                "body_pattern": self.request.body_pattern,
                "match_strategy": self.request.match_strategy.value,
            },
            "responses": [
                {
                    "status_code": r.status_code,
                    "headers": dict(r.headers),
                    "body": r.body,
                    "latency_ms": r.latency_ms,
                    "error": r.error,
                }
                for r in self.responses
            ],
            "mode": self.mode.value,
            "call_count": self.call_count,
        }

@dataclass
class RequestLog:
    """
    Record of a single request handled by the mock server.

    Fields:
        method: HTTP method of the request.
        path: Request path.
        headers: Request headers.
        body: Raw request body (if any).
        timestamp: When the request was received.
        matched_route: Name of the route that matched (None if 404).
        response_status: HTTP status code of the response returned.
    """

    method: str = ""
    path: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    body: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    matched_route: str | None = None
    response_status: int | None = None

# ---------------------------------------------------------------------------
# RequestMatcher
# ---------------------------------------------------------------------------

class RequestMatcher:
    """
    Evaluates whether an incoming request dictionary satisfies a
    ``MockRequest`` specification.

    The matcher checks:
    1. HTTP method equality (case-insensitive).
    2. Path matching according to the configured ``MatchStrategy``.
    3. Body pattern matching via regex when ``body_pattern`` is set.
    """

    def match(
        self,
        incoming_request: dict[str, Any],
        mock_request: MockRequest,
    ) -> bool:
        """
        Return ``True`` if *incoming_request* satisfies *mock_request*.

        Parameters:
            incoming_request: Dictionary with keys ``method``, ``path``,
                and optionally ``body``.
            mock_request: The specification to match against.
        """
        # --- Method -----------------------------------------------------------
        incoming_method = str(incoming_request.get("method", "")).upper()
        if incoming_method != mock_request.method.upper():
            return False

        # --- Path -------------------------------------------------------------
        incoming_path = str(incoming_request.get("path", ""))
        if not self._match_path(incoming_path, mock_request.path, mock_request.match_strategy):
            return False

        # --- Body pattern -----------------------------------------------------
        if mock_request.body_pattern is not None:
            incoming_body = incoming_request.get("body")
            if incoming_body is None:
                incoming_body = ""
            if not re.search(mock_request.body_pattern, str(incoming_body)):
                return False

        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _match_path(
        incoming_path: str,
        pattern: str,
        strategy: MatchStrategy,
    ) -> bool:
        """Compare *incoming_path* to *pattern* using *strategy*."""
        if strategy == MatchStrategy.EXACT:
            return incoming_path == pattern
        if strategy == MatchStrategy.PREFIX:
            return incoming_path.startswith(pattern)
        if strategy == MatchStrategy.REGEX:
            return re.search(pattern, incoming_path) is not None
        return False

# ---------------------------------------------------------------------------
# MockAPIServer
# ---------------------------------------------------------------------------

class MockAPIServer:
    """
    In-process mock HTTP server suitable for unit and integration testing.

    Routes are registered by name and matched in insertion order.  Every
    handled request is appended to an internal log that can later be
    inspected or asserted against.

    Usage::

        server = create_mock_server()

        server.add_route("get_users", MockRoute(
            request=MockRequest(method="GET", path="/api/users"),
            responses=[MockResponse(status_code=200, body='{"users": []}')],
        ))

        resp = server.handle_request("GET", "/api/users")
        assert resp.status_code == 200

        server.assert_called("get_users", times=1)
    """

    def __init__(self) -> None:
        self._routes: dict[str, MockRoute] = {}
        self._route_order: list[str] = []
        self._request_log: list[RequestLog] = []
        self._matcher = RequestMatcher()

    # ------------------------------------------------------------------
    # Route management
    # ------------------------------------------------------------------

    def add_route(self, name: str, route: MockRoute) -> None:
        """
        Register a named mock route.

        If a route with the same *name* already exists it is replaced and
        its position in the match order is preserved.
        """
        if name not in self._routes:
            self._route_order.append(name)
        self._routes[name] = route

    def remove_route(self, name: str) -> None:
        """
        Remove a named mock route.

        Raises ``KeyError`` if *name* is not registered.
        """
        if name not in self._routes:
            raise KeyError(f"Route '{name}' not found")
        del self._routes[name]
        self._route_order.remove(name)

    # ------------------------------------------------------------------
    # Request handling
    # ------------------------------------------------------------------

    def handle_request(
        self,
        method: str,
        path: str,
        headers: dict[str, str] | None = None,
        body: str | None = None,
    ) -> MockResponse:
        """
        Dispatch a request through registered routes and return a response.

        The routes are evaluated in insertion order.  The first matching
        route is selected.  If no route matches a default 404 response is
        returned.

        Parameters:
            method: HTTP method (e.g. ``"GET"``).
            path: Request path (e.g. ``"/api/users"``).
            headers: Optional request headers.
            body: Optional raw request body.

        Returns:
            A ``MockResponse`` instance.
        """
        if headers is None:
            headers = {}

        incoming = {
            "method": method,
            "path": path,
            "headers": headers,
            "body": body,
        }

        # Search for a matching route in insertion order.
        for route_name in self._route_order:
            route = self._routes[route_name]
            if self._matcher.match(incoming, route.request):
                route.call_count += 1
                response = self._select_response(route)

                self._request_log.append(
                    RequestLog(
                        method=method,
                        path=path,
                        headers=dict(headers),
                        body=body,
                        timestamp=datetime.now(),
                        matched_route=route_name,
                        response_status=response.status_code,
                    )
                )
                return response

        # No route matched -- return a default 404.
        default_response = MockResponse(
            status_code=404,
            body={"error": "No matching mock route found"},
        )
        self._request_log.append(
            RequestLog(
                method=method,
                path=path,
                headers=dict(headers),
                body=body,
                timestamp=datetime.now(),
                matched_route=None,
                response_status=404,
            )
        )
        return default_response

    # ------------------------------------------------------------------
    # Response selection helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _select_response(route: MockRoute) -> MockResponse:
        """
        Pick a response from *route* according to its ``mode``.

        - ``STATIC``: always returns the first response.
        - ``SEQUENCE``: round-robins through responses by call count.
        - ``RANDOM``: returns a random response.

        If the route has no responses a default 204 (No Content) is returned.
        """
        if not route.responses:
            return MockResponse(status_code=204)

        if route.mode == MockResponseMode.STATIC:
            return route.responses[0]

        if route.mode == MockResponseMode.SEQUENCE:
            index = (route.call_count - 1) % len(route.responses)
            return route.responses[index]

        if route.mode == MockResponseMode.RANDOM:
            return _random.choice(route.responses)

        # Fallback (should not happen with a valid enum value).
        return route.responses[0]

    # ------------------------------------------------------------------
    # Request log
    # ------------------------------------------------------------------

    def get_request_log(self) -> list[RequestLog]:
        """Return a copy of the request log."""
        return list(self._request_log)

    def clear_log(self) -> None:
        """Clear the request log."""
        self._request_log.clear()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Clear all routes, reset call counts, and clear the request log.
        """
        self._routes.clear()
        self._route_order.clear()
        self._request_log.clear()

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------

    def assert_called(
        self,
        route_name: str,
        times: int | None = None,
    ) -> None:
        """
        Assert that a route was called.

        Parameters:
            route_name: Name of the route to check.
            times: If given, assert the route was called exactly this many
                times.

        Raises:
            AssertionError: If the assertion fails.
            KeyError: If the route name is not registered.
        """
        if route_name not in self._routes:
            raise KeyError(f"Route '{route_name}' not found")

        route = self._routes[route_name]

        if route.call_count == 0:
            raise AssertionError(
                f"Expected route '{route_name}' to have been called, "
                f"but it was never called"
            )

        if times is not None and route.call_count != times:
            raise AssertionError(
                f"Expected route '{route_name}' to have been called "
                f"{times} time(s), but it was called {route.call_count} time(s)"
            )

    def assert_not_called(self, route_name: str) -> None:
        """
        Assert that a route was *not* called.

        Raises:
            AssertionError: If the route was called at least once.
            KeyError: If the route name is not registered.
        """
        if route_name not in self._routes:
            raise KeyError(f"Route '{route_name}' not found")

        route = self._routes[route_name]
        if route.call_count != 0:
            raise AssertionError(
                f"Expected route '{route_name}' to not have been called, "
                f"but it was called {route.call_count} time(s)"
            )

# ---------------------------------------------------------------------------
# ResponseFixture
# ---------------------------------------------------------------------------

class ResponseFixture:
    """
    Convenience factory with static methods for common HTTP responses.

    Usage::

        fixture = create_fixture()
        ok = fixture.success(body={"status": "ok"})
        err = fixture.server_error()
    """

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
    def json_response(
        data: Any,
        status_code: int = 200,
    ) -> MockResponse:
        """
        Return a response with a JSON-serialized body and the appropriate
        ``Content-Type`` header.
        """
        return MockResponse(
            status_code=status_code,
            headers={"Content-Type": "application/json"},
            body=json.dumps(data),
        )

# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------

def create_mock_server() -> MockAPIServer:
    """Create and return a new ``MockAPIServer`` instance."""
    return MockAPIServer()

def create_fixture() -> ResponseFixture:
    """Create and return a new ``ResponseFixture`` instance."""
    return ResponseFixture()

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    # Enums
    "MatchStrategy",
    "MockResponseMode",
    # Dataclasses
    "MockRequest",
    "MockResponse",
    "MockRoute",
    "RequestLog",
    # Classes
    "RequestMatcher",
    "MockAPIServer",
    "ResponseFixture",
    # Factory functions
    "create_mock_server",
    "create_fixture",
]
