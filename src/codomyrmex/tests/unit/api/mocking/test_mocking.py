"""Comprehensive tests for the codomyrmex.api.mocking module.

Covers enums, dataclasses, request matching, mock server routing with
multiple response modes, request logging, assertion helpers, response
fixtures, and factory functions.
"""

import json

import pytest

from codomyrmex.api.mocking import (
    MatchStrategy,
    MockAPIServer,
    MockRequest,
    MockResponse,
    MockResponseMode,
    MockRoute,
    RequestLog,
    RequestMatcher,
    ResponseFixture,
    create_fixture,
    create_mock_server,
)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestMatchStrategy:
    """Verify MatchStrategy enum members and values."""

    def test_exact_member(self):
        assert MatchStrategy.EXACT.value == "exact"

    def test_prefix_member(self):
        assert MatchStrategy.PREFIX.value == "prefix"

    def test_regex_member(self):
        assert MatchStrategy.REGEX.value == "regex"

    def test_member_count(self):
        assert len(MatchStrategy) == 3


class TestMockResponseMode:
    """Verify MockResponseMode enum members."""

    def test_static_member(self):
        assert MockResponseMode.STATIC.value == "static"

    def test_sequence_member(self):
        assert MockResponseMode.SEQUENCE.value == "sequence"

    def test_random_member(self):
        assert MockResponseMode.RANDOM.value == "random"


# ---------------------------------------------------------------------------
# Dataclasses -- defaults
# ---------------------------------------------------------------------------


class TestMockRequest:
    """Verify MockRequest default field values."""

    def test_defaults(self):
        req = MockRequest()
        assert req.method == "GET"
        assert req.path == "/"
        assert req.headers == {}
        assert req.query_params == {}
        assert req.body_pattern is None
        assert req.match_strategy == MatchStrategy.EXACT

    def test_custom_values(self):
        req = MockRequest(method="POST", path="/api/data", body_pattern=".*id.*")
        assert req.method == "POST"
        assert req.path == "/api/data"
        assert req.body_pattern == ".*id.*"


class TestMockResponse:
    """Verify MockResponse default field values."""

    def test_defaults(self):
        resp = MockResponse()
        assert resp.status_code == 200
        assert resp.headers == {}
        assert resp.body is None
        assert resp.latency_ms == 0.0
        assert resp.error is None

    def test_custom_values(self):
        resp = MockResponse(status_code=500, body="fail", error="boom")
        assert resp.status_code == 500
        assert resp.body == "fail"
        assert resp.error == "boom"


class TestMockRoute:
    """Verify MockRoute defaults and serialization."""

    def test_defaults(self):
        route = MockRoute()
        assert isinstance(route.request, MockRequest)
        assert route.responses == []
        assert route.mode == MockResponseMode.STATIC
        assert route.call_count == 0

    def test_to_dict(self):
        route = MockRoute(
            request=MockRequest(method="POST", path="/items"),
            responses=[MockResponse(status_code=201, body="created")],
            mode=MockResponseMode.SEQUENCE,
            call_count=5,
        )
        d = route.to_dict()

        assert d["request"]["method"] == "POST"
        assert d["request"]["path"] == "/items"
        assert d["request"]["match_strategy"] == "exact"
        assert d["mode"] == "sequence"
        assert d["call_count"] == 5
        assert len(d["responses"]) == 1
        assert d["responses"][0]["status_code"] == 201
        assert d["responses"][0]["body"] == "created"

    def test_to_dict_empty_responses(self):
        d = MockRoute().to_dict()
        assert d["responses"] == []


# ---------------------------------------------------------------------------
# RequestMatcher
# ---------------------------------------------------------------------------


class TestRequestMatcher:
    """Verify request matching across strategies and edge cases."""

    @pytest.fixture()
    def matcher(self):
        return RequestMatcher()

    # -- Exact match -------------------------------------------------------

    def test_exact_match_success(self, matcher):
        incoming = {"method": "GET", "path": "/users"}
        spec = MockRequest(method="GET", path="/users", match_strategy=MatchStrategy.EXACT)
        assert matcher.match(incoming, spec) is True

    def test_exact_match_failure(self, matcher):
        incoming = {"method": "GET", "path": "/users/1"}
        spec = MockRequest(method="GET", path="/users", match_strategy=MatchStrategy.EXACT)
        assert matcher.match(incoming, spec) is False

    # -- Prefix match ------------------------------------------------------

    def test_prefix_match_success(self, matcher):
        incoming = {"method": "GET", "path": "/api/v1/users"}
        spec = MockRequest(method="GET", path="/api/v1", match_strategy=MatchStrategy.PREFIX)
        assert matcher.match(incoming, spec) is True

    def test_prefix_match_exact_path(self, matcher):
        incoming = {"method": "GET", "path": "/api"}
        spec = MockRequest(method="GET", path="/api", match_strategy=MatchStrategy.PREFIX)
        assert matcher.match(incoming, spec) is True

    # -- Regex match -------------------------------------------------------

    def test_regex_match_success(self, matcher):
        incoming = {"method": "GET", "path": "/users/42"}
        spec = MockRequest(
            method="GET",
            path=r"/users/\d+",
            match_strategy=MatchStrategy.REGEX,
        )
        assert matcher.match(incoming, spec) is True

    def test_regex_match_failure(self, matcher):
        incoming = {"method": "GET", "path": "/users/abc"}
        spec = MockRequest(
            method="GET",
            path=r"^/users/\d+$",
            match_strategy=MatchStrategy.REGEX,
        )
        assert matcher.match(incoming, spec) is False

    # -- Method mismatch ---------------------------------------------------

    def test_method_mismatch(self, matcher):
        incoming = {"method": "POST", "path": "/users"}
        spec = MockRequest(method="GET", path="/users")
        assert matcher.match(incoming, spec) is False

    def test_method_case_insensitive(self, matcher):
        incoming = {"method": "get", "path": "/"}
        spec = MockRequest(method="GET", path="/")
        assert matcher.match(incoming, spec) is True

    # -- Body pattern ------------------------------------------------------

    def test_body_pattern_match(self, matcher):
        incoming = {"method": "POST", "path": "/data", "body": '{"id": 123}'}
        spec = MockRequest(method="POST", path="/data", body_pattern=r'"id":\s*\d+')
        assert matcher.match(incoming, spec) is True

    def test_body_pattern_mismatch(self, matcher):
        incoming = {"method": "POST", "path": "/data", "body": '{"name": "test"}'}
        spec = MockRequest(method="POST", path="/data", body_pattern=r'"id":\s*\d+')
        assert matcher.match(incoming, spec) is False

    def test_body_pattern_with_no_body(self, matcher):
        incoming = {"method": "POST", "path": "/data"}
        spec = MockRequest(method="POST", path="/data", body_pattern=r"something")
        assert matcher.match(incoming, spec) is False


# ---------------------------------------------------------------------------
# MockAPIServer
# ---------------------------------------------------------------------------


class TestMockAPIServer:
    """Verify route management, request handling, logging, and assertions."""

    @pytest.fixture()
    def server(self):
        return MockAPIServer()

    @pytest.fixture()
    def route_200(self):
        return MockRoute(
            request=MockRequest(method="GET", path="/ok"),
            responses=[MockResponse(status_code=200, body="ok")],
        )

    # -- Route management --------------------------------------------------

    def test_add_route(self, server, route_200):
        server.add_route("ok_route", route_200)
        resp = server.handle_request("GET", "/ok")
        assert resp.status_code == 200

    def test_remove_route(self, server, route_200):
        server.add_route("ok_route", route_200)
        server.remove_route("ok_route")
        resp = server.handle_request("GET", "/ok")
        assert resp.status_code == 404

    def test_remove_nonexistent_route_raises(self, server):
        with pytest.raises(KeyError, match="not found"):
            server.remove_route("ghost")

    # -- handle_request: match vs. no-match --------------------------------

    def test_handle_request_match(self, server, route_200):
        server.add_route("ok_route", route_200)
        resp = server.handle_request("GET", "/ok")
        assert resp.status_code == 200
        assert resp.body == "ok"

    def test_handle_request_no_match_returns_404(self, server):
        resp = server.handle_request("GET", "/nope")
        assert resp.status_code == 404
        assert resp.body == {"error": "No matching mock route found"}

    # -- Response modes ----------------------------------------------------

    def test_static_mode_always_returns_first(self, server):
        route = MockRoute(
            request=MockRequest(method="GET", path="/s"),
            responses=[
                MockResponse(status_code=200, body="first"),
                MockResponse(status_code=201, body="second"),
            ],
            mode=MockResponseMode.STATIC,
        )
        server.add_route("static", route)
        for _ in range(3):
            resp = server.handle_request("GET", "/s")
            assert resp.status_code == 200
            assert resp.body == "first"

    def test_sequence_mode_round_robins(self, server):
        route = MockRoute(
            request=MockRequest(method="GET", path="/seq"),
            responses=[
                MockResponse(status_code=200, body="a"),
                MockResponse(status_code=201, body="b"),
                MockResponse(status_code=202, body="c"),
            ],
            mode=MockResponseMode.SEQUENCE,
        )
        server.add_route("seq", route)
        codes = [server.handle_request("GET", "/seq").status_code for _ in range(6)]
        assert codes == [200, 201, 202, 200, 201, 202]

    def test_random_mode_returns_valid_responses(self, server):
        responses = [
            MockResponse(status_code=200, body="x"),
            MockResponse(status_code=201, body="y"),
        ]
        route = MockRoute(
            request=MockRequest(method="GET", path="/rand"),
            responses=responses,
            mode=MockResponseMode.RANDOM,
        )
        server.add_route("rand", route)
        seen_codes = {server.handle_request("GET", "/rand").status_code for _ in range(20)}
        assert seen_codes.issubset({200, 201})

    def test_no_responses_returns_204(self, server):
        route = MockRoute(
            request=MockRequest(method="GET", path="/empty"),
            responses=[],
        )
        server.add_route("empty", route)
        resp = server.handle_request("GET", "/empty")
        assert resp.status_code == 204

    # -- Request log -------------------------------------------------------

    def test_request_log_records_entries(self, server, route_200):
        server.add_route("ok_route", route_200)
        server.handle_request("GET", "/ok")
        server.handle_request("GET", "/missing")

        log = server.get_request_log()
        assert len(log) == 2
        assert log[0].matched_route == "ok_route"
        assert log[0].response_status == 200
        assert log[1].matched_route is None
        assert log[1].response_status == 404

    def test_clear_log(self, server, route_200):
        server.add_route("ok_route", route_200)
        server.handle_request("GET", "/ok")
        assert len(server.get_request_log()) == 1

        server.clear_log()
        assert len(server.get_request_log()) == 0

    # -- Reset -------------------------------------------------------------

    def test_reset_clears_everything(self, server, route_200):
        server.add_route("ok_route", route_200)
        server.handle_request("GET", "/ok")
        server.reset()

        assert server.get_request_log() == []
        resp = server.handle_request("GET", "/ok")
        assert resp.status_code == 404

    # -- assert_called / assert_not_called ---------------------------------

    def test_assert_called_success(self, server, route_200):
        server.add_route("ok_route", route_200)
        server.handle_request("GET", "/ok")
        server.assert_called("ok_route")
        server.assert_called("ok_route", times=1)

    def test_assert_called_failure_never_called(self, server, route_200):
        server.add_route("ok_route", route_200)
        with pytest.raises(AssertionError, match="never called"):
            server.assert_called("ok_route")

    def test_assert_called_failure_wrong_count(self, server, route_200):
        server.add_route("ok_route", route_200)
        server.handle_request("GET", "/ok")
        with pytest.raises(AssertionError, match="1 time"):
            server.assert_called("ok_route", times=3)

    def test_assert_called_unknown_route_raises(self, server):
        with pytest.raises(KeyError, match="not found"):
            server.assert_called("ghost")

    def test_assert_not_called_success(self, server, route_200):
        server.add_route("ok_route", route_200)
        server.assert_not_called("ok_route")

    def test_assert_not_called_failure(self, server, route_200):
        server.add_route("ok_route", route_200)
        server.handle_request("GET", "/ok")
        with pytest.raises(AssertionError, match="was called"):
            server.assert_not_called("ok_route")

    def test_assert_not_called_unknown_route_raises(self, server):
        with pytest.raises(KeyError, match="not found"):
            server.assert_not_called("ghost")


# ---------------------------------------------------------------------------
# ResponseFixture
# ---------------------------------------------------------------------------


class TestResponseFixture:
    """Verify convenience response factory methods."""

    @pytest.fixture()
    def fixture(self):
        return ResponseFixture()

    def test_success(self, fixture):
        resp = fixture.success(body={"ok": True})
        assert resp.status_code == 200
        assert resp.body == {"ok": True}

    def test_not_found(self, fixture):
        resp = fixture.not_found()
        assert resp.status_code == 404
        assert resp.body == {"error": "Not Found"}

    def test_server_error(self, fixture):
        resp = fixture.server_error()
        assert resp.status_code == 500
        assert resp.body == {"error": "Internal Server Error"}

    def test_unauthorized(self, fixture):
        resp = fixture.unauthorized()
        assert resp.status_code == 401
        assert resp.body == {"error": "Unauthorized"}

    def test_rate_limited_default(self, fixture):
        resp = fixture.rate_limited()
        assert resp.status_code == 429
        assert resp.headers["Retry-After"] == "60"
        assert resp.body == {"error": "Too Many Requests"}

    def test_rate_limited_custom_retry(self, fixture):
        resp = fixture.rate_limited(retry_after=120)
        assert resp.headers["Retry-After"] == "120"

    def test_json_response(self, fixture):
        data = {"users": [1, 2, 3]}
        resp = fixture.json_response(data)
        assert resp.status_code == 200
        assert resp.headers["Content-Type"] == "application/json"
        assert json.loads(resp.body) == data

    def test_json_response_custom_status(self, fixture):
        resp = fixture.json_response({"created": True}, status_code=201)
        assert resp.status_code == 201
        assert resp.headers["Content-Type"] == "application/json"


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------


class TestFactories:
    """Verify module-level factory helpers."""

    def test_create_mock_server_returns_server(self):
        server = create_mock_server()
        assert isinstance(server, MockAPIServer)

    def test_create_mock_server_independent_instances(self):
        s1 = create_mock_server()
        s2 = create_mock_server()
        s1.add_route("r", MockRoute())
        assert s2.get_request_log() == []

    def test_create_fixture_returns_fixture(self):
        f = create_fixture()
        assert isinstance(f, ResponseFixture)
