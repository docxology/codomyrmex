"""MockAPIServer implementation for the API mocking module."""

import random as _random
from datetime import datetime
from typing import Any

from .models import (
    MatchStrategy,
    MockRequest,
    MockResponse,
    MockResponseMode,
    MockRoute,
    RequestLog,
    RequestMatcher,
)


class MockAPIServer:
    """In-process mock HTTP server suitable for unit and integration testing."""

    def __init__(self) -> None:
        self._routes: dict[str, MockRoute] = {}
        self._route_order: list[str] = []
        self._request_log: list[RequestLog] = []
        self._matcher = RequestMatcher()

    def add_route(self, name: str, route: MockRoute) -> None:
        """Register a named mock route."""
        if name not in self._routes:
            self._route_order.append(name)
        self._routes[name] = route

    def remove_route(self, name: str) -> None:
        """Remove a named mock route. Raises KeyError if not registered."""
        if name not in self._routes:
            raise KeyError(f"Route '{name}' not found")
        del self._routes[name]
        self._route_order.remove(name)

    def handle_request(
        self,
        method: str,
        path: str,
        headers: dict[str, str] | None = None,
        body: str | None = None,
    ) -> MockResponse:
        """Dispatch a request through registered routes and return a response."""
        if headers is None:
            headers = {}

        incoming: dict[str, Any] = {
            "method": method,
            "path": path,
            "headers": headers,
            "body": body,
        }

        for route_name in self._route_order:
            route = self._routes[route_name]
            if self._matcher.match(incoming, route.request):
                route.call_count += 1
                response = self._select_response(route)
                self._log_request(method, path, headers, body, route_name, response.status_code)
                return response

        self._log_request(method, path, headers, body, None, 404)
        return MockResponse(status_code=404, body={"error": "No matching mock route found"})

    def _log_request(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        body: str | None,
        matched_route: str | None,
        status_code: int,
    ) -> None:
        """Append a RequestLog entry for a handled request."""
        self._request_log.append(
            RequestLog(
                method=method,
                path=path,
                headers=dict(headers),
                body=body,
                timestamp=datetime.now(),
                matched_route=matched_route,
                response_status=status_code,
            )
        )

    @staticmethod
    def _select_response(route: MockRoute) -> MockResponse:
        """Pick a response from route according to its mode."""
        if not route.responses:
            return MockResponse(status_code=204)
        if route.mode == MockResponseMode.STATIC:
            return route.responses[0]
        if route.mode == MockResponseMode.SEQUENCE:
            index = (route.call_count - 1) % len(route.responses)
            return route.responses[index]
        if route.mode == MockResponseMode.RANDOM:
            return _random.choice(route.responses)
        return route.responses[0]

    def get_request_log(self) -> list[RequestLog]:
        """Return a copy of the request log."""
        return list(self._request_log)

    def clear_log(self) -> None:
        """Clear the request log."""
        self._request_log.clear()

    def reset(self) -> None:
        """Clear all routes, reset call counts, and clear the request log."""
        self._routes.clear()
        self._route_order.clear()
        self._request_log.clear()

    def assert_called(self, route_name: str, times: int | None = None) -> None:
        """Assert that a route was called."""
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
        """Assert that a route was not called."""
        if route_name not in self._routes:
            raise KeyError(f"Route '{route_name}' not found")
        route = self._routes[route_name]
        if route.call_count != 0:
            raise AssertionError(
                f"Expected route '{route_name}' to not have been called, "
                f"but it was called {route.call_count} time(s)"
            )
