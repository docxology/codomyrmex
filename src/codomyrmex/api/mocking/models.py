"""Data models for the API mocking module."""

import random as _random
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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


@dataclass
class MockRequest:
    """Specification for matching incoming requests."""

    method: str = "GET"
    path: str = "/"
    headers: dict[str, str] = field(default_factory=dict)
    query_params: dict[str, str] = field(default_factory=dict)
    body_pattern: str | None = None
    match_strategy: MatchStrategy = MatchStrategy.EXACT


@dataclass
class MockResponse:
    """A canned response returned by the mock server."""

    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    body: Any = None
    latency_ms: float = 0.0
    error: str | None = None


@dataclass
class MockRoute:
    """Binds a request specification to one or more possible responses."""

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
    """Record of a single request handled by the mock server."""

    method: str = ""
    path: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    body: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    matched_route: str | None = None
    response_status: int | None = None


class RequestMatcher:
    """Evaluates whether an incoming request dictionary satisfies a MockRequest."""

    def match(
        self,
        incoming_request: dict[str, Any],
        mock_request: MockRequest,
    ) -> bool:
        """Return True if incoming_request satisfies mock_request."""
        incoming_method = str(incoming_request.get("method", "")).upper()
        if incoming_method != mock_request.method.upper():
            return False

        incoming_path = str(incoming_request.get("path", ""))
        if not self._match_path(
            incoming_path, mock_request.path, mock_request.match_strategy
        ):
            return False

        if mock_request.body_pattern is not None:
            incoming_body = incoming_request.get("body")
            if incoming_body is None:
                incoming_body = ""
            if not re.search(mock_request.body_pattern, str(incoming_body)):
                return False

        return True

    @staticmethod
    def _match_path(
        incoming_path: str,
        pattern: str,
        strategy: MatchStrategy,
    ) -> bool:
        """Compare incoming_path to pattern using strategy."""
        if strategy == MatchStrategy.EXACT:
            return incoming_path == pattern
        if strategy == MatchStrategy.PREFIX:
            return incoming_path.startswith(pattern)
        if strategy == MatchStrategy.REGEX:
            return re.search(pattern, incoming_path) is not None
        return False
