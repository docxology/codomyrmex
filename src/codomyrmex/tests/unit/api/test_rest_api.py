"""Unit tests for codomyrmex.api.standardization.rest_api.

Imports the submodule file directly to avoid the circular import chain
introduced by codomyrmex.api.__init__ → api/documentation → api/openapi_generator
→ api/standardization/__init__ → api/openapi_generator (cycle).

No mocks are used.  All test doubles are real concrete subclasses or callable
objects.
"""

import importlib.util
import json
import sys

import pytest

# ---------------------------------------------------------------------------
# Direct-import helper — load rest_api.py without triggering parent __init__
# ---------------------------------------------------------------------------

def _load_rest_api():
    """Load rest_api module directly, bypassing the circular-import chain."""
    name = "codomyrmex.api.standardization.rest_api"
    if name in sys.modules:
        return sys.modules[name]
    import codomyrmex.logging_monitoring  # noqa: F401 — loads cleanly, no cycles
    spec = importlib.util.spec_from_file_location(
        name,
        "src/codomyrmex/api/standardization/rest_api.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


try:
    _rest_api_mod = _load_rest_api()
    HTTPMethod = _rest_api_mod.HTTPMethod
    HTTPStatus = _rest_api_mod.HTTPStatus
    APIRequest = _rest_api_mod.APIRequest
    APIResponse = _rest_api_mod.APIResponse
    APIEndpoint = _rest_api_mod.APIEndpoint
    APIRouter = _rest_api_mod.APIRouter
    RESTAPI = _rest_api_mod.RESTAPI
    create_api = _rest_api_mod.create_api
    create_router = _rest_api_mod.create_router
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    _SKIP_REASON = str(_exc)

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason=f"rest_api unavailable: {'' if _AVAILABLE else _SKIP_REASON}",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_router():
    """A router with a single GET /hello endpoint."""
    router = APIRouter(prefix="/api")

    @router.get("/hello", summary="Say hello")
    def hello_handler(request: APIRequest) -> APIResponse:
        return APIResponse.success({"message": "hello"})

    return router


@pytest.fixture()
def rest_api():
    """A RESTAPI instance with a basic echo endpoint registered."""
    api = create_api(title="TestAPI", version="0.1.0")
    router = create_router(prefix="/v1")

    @router.get("/ping")
    def ping(request: APIRequest) -> APIResponse:
        return APIResponse.success({"pong": True})

    @router.post("/echo")
    def echo(request: APIRequest) -> APIResponse:
        body = request.json_body or {}
        return APIResponse.success(body)

    @router.get("/users/{user_id}")
    def get_user(request: APIRequest) -> APIResponse:
        return APIResponse.success({"id": request.path_params.get("user_id")})

    api.add_router(router)
    return api


# ===========================================================================
# HTTPMethod
# ===========================================================================

class TestHTTPMethod:
    """HTTPMethod enum — all seven verbs must be present and have correct values."""

    def test_get_value(self):
        assert HTTPMethod.GET.value == "GET"

    def test_post_value(self):
        assert HTTPMethod.POST.value == "POST"

    def test_put_value(self):
        assert HTTPMethod.PUT.value == "PUT"

    def test_delete_value(self):
        assert HTTPMethod.DELETE.value == "DELETE"

    def test_patch_value(self):
        assert HTTPMethod.PATCH.value == "PATCH"

    def test_options_value(self):
        assert HTTPMethod.OPTIONS.value == "OPTIONS"

    def test_head_value(self):
        assert HTTPMethod.HEAD.value == "HEAD"

    def test_enum_has_seven_members(self):
        assert len(HTTPMethod) == 7

    def test_construct_from_string(self):
        assert HTTPMethod("POST") == HTTPMethod.POST


# ===========================================================================
# HTTPStatus
# ===========================================================================

class TestHTTPStatus:
    """HTTPStatus enum — spot-check key codes."""

    def test_ok_is_200(self):
        assert HTTPStatus.OK.value == 200

    def test_created_is_201(self):
        assert HTTPStatus.CREATED.value == 201

    def test_not_found_is_404(self):
        assert HTTPStatus.NOT_FOUND.value == 404

    def test_bad_request_is_400(self):
        assert HTTPStatus.BAD_REQUEST.value == 400

    def test_internal_server_error_is_500(self):
        assert HTTPStatus.INTERNAL_SERVER_ERROR.value == 500

    def test_no_content_is_204(self):
        assert HTTPStatus.NO_CONTENT.value == 204


# ===========================================================================
# APIRequest
# ===========================================================================

class TestAPIRequest:
    """APIRequest dataclass — construction, json_body parsing, defaults."""

    def test_basic_construction(self):
        req = APIRequest(method=HTTPMethod.GET, path="/test")
        assert req.method == HTTPMethod.GET
        assert req.path == "/test"
        assert req.headers == {}
        assert req.query_params == {}
        assert req.body is None
        assert req.path_params == {}

    def test_json_body_parses_valid_json(self):
        body = json.dumps({"key": "value"}).encode()
        req = APIRequest(method=HTTPMethod.POST, path="/data", body=body)
        assert req.json_body == {"key": "value"}

    def test_json_body_returns_none_for_no_body(self):
        req = APIRequest(method=HTTPMethod.GET, path="/")
        assert req.json_body is None

    def test_json_body_returns_none_for_invalid_json(self):
        req = APIRequest(method=HTTPMethod.POST, path="/", body=b"not-json{{{{")
        assert req.json_body is None

    def test_json_body_handles_unicode_error(self):
        # Invalid UTF-8 bytes
        req = APIRequest(method=HTTPMethod.POST, path="/", body=b"\xff\xfe")
        assert req.json_body is None

    def test_context_default_is_empty_dict(self):
        req = APIRequest(method=HTTPMethod.GET, path="/")
        assert req.context == {}

    def test_path_params_can_be_set(self):
        req = APIRequest(method=HTTPMethod.GET, path="/users/42")
        req.path_params = {"user_id": "42"}
        assert req.path_params["user_id"] == "42"


# ===========================================================================
# APIResponse
# ===========================================================================

class TestAPIResponse:
    """APIResponse dataclass — construction, factory methods, headers."""

    def test_basic_construction(self):
        resp = APIResponse(status_code=HTTPStatus.OK, body={"a": 1})
        assert resp.status_code == HTTPStatus.OK
        assert resp.body == {"a": 1}
        assert "Content-Type" in resp.headers

    def test_content_type_header_set_automatically(self):
        resp = APIResponse(status_code=HTTPStatus.OK, content_type="text/plain")
        assert resp.headers["Content-Type"] == "text/plain"

    def test_success_factory_default_status(self):
        resp = APIResponse.success({"ok": True})
        assert resp.status_code == HTTPStatus.OK
        assert resp.body == {"ok": True}

    def test_success_factory_custom_status(self):
        resp = APIResponse.success(None, HTTPStatus.CREATED)
        assert resp.status_code == HTTPStatus.CREATED

    def test_error_factory(self):
        resp = APIResponse.error("oops")
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.body["error"] == "oops"
        assert resp.body["status_code"] == 500

    def test_error_factory_custom_status(self):
        resp = APIResponse.error("not found", HTTPStatus.NOT_FOUND)
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert resp.body["status_code"] == 404

    def test_not_found_factory(self):
        resp = APIResponse.not_found("Widget")
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert "Widget" in resp.body["error"]

    def test_not_found_factory_default_resource(self):
        resp = APIResponse.not_found()
        assert "Resource" in resp.body["error"]

    def test_bad_request_factory(self):
        resp = APIResponse.bad_request("missing field")
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert "missing field" in resp.body["error"]

    def test_bad_request_factory_default_message(self):
        resp = APIResponse.bad_request()
        assert resp.status_code == HTTPStatus.BAD_REQUEST


# ===========================================================================
# APIRouter
# ===========================================================================

class TestAPIRouter:
    """APIRouter — endpoint registration, normalization, matching."""

    def test_empty_router_has_no_endpoints(self):
        router = APIRouter()
        assert router.get_all_endpoints() == []

    def test_prefix_is_stripped_of_trailing_slash(self):
        router = APIRouter(prefix="/api/v1/")
        assert router.prefix == "/api/v1"

    def test_add_endpoint_registers_correctly(self):
        router = APIRouter()

        def handler(req):
            return APIResponse.success()

        ep = APIEndpoint(
            path="/items",
            method=HTTPMethod.GET,
            handler=handler,
        )
        router.add_endpoint(ep)
        assert len(router.get_all_endpoints()) == 1

    def test_get_decorator_registers_endpoint(self, simple_router):
        endpoints = simple_router.get_all_endpoints()
        assert len(endpoints) == 1
        ep = endpoints[0]
        assert ep.method == HTTPMethod.GET
        assert ep.path.endswith("/hello")

    def test_post_decorator_registers_endpoint(self):
        router = APIRouter()

        @router.post("/submit")
        def submit(req):
            return APIResponse.success()

        endpoints = router.get_all_endpoints()
        assert any(e.method == HTTPMethod.POST for e in endpoints)

    def test_put_decorator(self):
        router = APIRouter()

        @router.put("/item")
        def update(req):
            return APIResponse.success()

        eps = router.get_all_endpoints()
        assert eps[0].method == HTTPMethod.PUT

    def test_delete_decorator(self):
        router = APIRouter()

        @router.delete("/item/{id}")
        def delete(req):
            return APIResponse.success()

        eps = router.get_all_endpoints()
        assert eps[0].method == HTTPMethod.DELETE

    def test_patch_decorator(self):
        router = APIRouter()

        @router.patch("/item/{id}")
        def patch(req):
            return APIResponse.success()

        eps = router.get_all_endpoints()
        assert eps[0].method == HTTPMethod.PATCH

    def test_path_normalized_with_leading_slash(self):
        router = APIRouter()

        @router.get("no-leading-slash")
        def handler(req):
            return APIResponse.success()

        ep = router.get_all_endpoints()[0]
        assert ep.path.startswith("/")

    def test_prefix_prepended_to_path(self):
        router = APIRouter(prefix="/v2")

        @router.get("/resource")
        def handler(req):
            return APIResponse.success()

        ep = router.get_all_endpoints()[0]
        assert ep.path == "/v2/resource"

    def test_match_exact_path(self):
        router = APIRouter()

        @router.get("/exact")
        def handler(req):
            return APIResponse.success()

        result = router.match_endpoint(HTTPMethod.GET, "/exact")
        assert result is not None
        endpoint, params = result
        assert endpoint.path == "/exact"
        assert params == {}

    def test_match_returns_none_for_unknown_path(self):
        router = APIRouter()
        assert router.match_endpoint(HTTPMethod.GET, "/unknown") is None

    def test_match_parametrized_path(self):
        router = APIRouter()

        @router.get("/users/{user_id}")
        def handler(req):
            return APIResponse.success()

        result = router.match_endpoint(HTTPMethod.GET, "/users/42")
        assert result is not None
        endpoint, params = result
        assert params["user_id"] == "42"

    def test_match_multiple_params(self):
        router = APIRouter()

        @router.get("/orgs/{org}/repos/{repo}")
        def handler(req):
            return APIResponse.success()

        result = router.match_endpoint(HTTPMethod.GET, "/orgs/acme/repos/widget")
        assert result is not None
        _, params = result
        assert params["org"] == "acme"
        assert params["repo"] == "widget"

    def test_match_method_mismatch_returns_none(self):
        router = APIRouter()

        @router.get("/only-get")
        def handler(req):
            return APIResponse.success()

        assert router.match_endpoint(HTTPMethod.POST, "/only-get") is None

    def test_sub_router_endpoints_accessible(self):
        parent = APIRouter(prefix="/parent")
        child = APIRouter(prefix="/child")

        @child.get("/leaf")
        def handler(req):
            return APIResponse.success()

        parent.add_router(child)
        all_eps = parent.get_all_endpoints()
        assert len(all_eps) == 1

    def test_sub_router_match_works(self):
        parent = APIRouter()
        child = APIRouter(prefix="/sub")

        @child.get("/item")
        def handler(req):
            return APIResponse.success()

        parent.add_router(child)
        result = parent.match_endpoint(HTTPMethod.GET, "/sub/item")
        assert result is not None

    def test_add_middleware(self):
        router = APIRouter()

        def mw(req):
            return None

        router.add_middleware(mw)
        assert mw in router.middleware


# ===========================================================================
# RESTAPI
# ===========================================================================

class TestRESTAPI:
    """RESTAPI — handle_request, metrics, OPTIONS middleware."""

    def test_create_api_factory(self):
        api = create_api(title="MyAPI", version="2.0")
        assert api.title == "MyAPI"
        assert api.version == "2.0"

    def test_initial_metrics_zero(self):
        api = create_api()
        m = api.get_metrics()
        assert m["total_requests"] == 0
        assert m["total_errors"] == 0

    def test_handle_get_registered_endpoint(self, rest_api):
        resp = rest_api.handle_request("GET", "/v1/ping")
        assert resp.status_code == HTTPStatus.OK

    def test_handle_unknown_endpoint_returns_404(self, rest_api):
        resp = rest_api.handle_request("GET", "/v1/nonexistent")
        assert resp.status_code == HTTPStatus.NOT_FOUND

    def test_handle_invalid_method_returns_405(self, rest_api):
        resp = rest_api.handle_request("INVALID_VERB", "/v1/ping")
        assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_handle_post_with_json_body(self, rest_api):
        body = json.dumps({"data": "test"}).encode()
        resp = rest_api.handle_request("POST", "/v1/echo", body=body)
        assert resp.status_code == HTTPStatus.OK
        assert resp.body == {"data": "test"}

    def test_handle_options_returns_cors_headers(self, rest_api):
        resp = rest_api.handle_request("OPTIONS", "/v1/any")
        assert resp.status_code == HTTPStatus.OK
        assert "Access-Control-Allow-Origin" in resp.headers

    def test_handle_path_params(self, rest_api):
        resp = rest_api.handle_request("GET", "/v1/users/99")
        assert resp.status_code == HTTPStatus.OK
        assert resp.body["id"] == "99"

    def test_request_count_increments(self, rest_api):
        rest_api.handle_request("GET", "/v1/ping")
        rest_api.handle_request("GET", "/v1/ping")
        assert rest_api.request_count == 2

    def test_error_count_increments_on_handler_exception(self):
        api = create_api()
        router = create_router()

        @router.get("/boom")
        def boom(req):
            raise RuntimeError("deliberate failure")

        api.add_router(router)
        resp = api.handle_request("GET", "/boom")
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert api.error_count == 1

    def test_query_string_parsed_into_query_params(self):
        """Query params are parsed and accessible via the request object."""
        captured = {}

        api = create_api()
        router = create_router()

        @router.get("/search")
        def search(req):
            captured.update(req.query_params)
            return APIResponse.success({})

        api.add_router(router)
        api.handle_request("GET", "/search", query_string="q=hello&page=1")
        assert "q" in captured
        assert captured["q"] == ["hello"]

    def test_get_endpoints_returns_registered(self, rest_api):
        endpoints = rest_api.get_endpoints()
        paths = [e.path for e in endpoints]
        assert "/v1/ping" in paths
        assert "/v1/echo" in paths

    def test_metrics_error_rate_formula(self):
        api = create_api()
        # No requests yet — error_rate denominator is max(0,1)=1
        m = api.get_metrics()
        assert m["error_rate"] == 0.0

    def test_handler_returning_non_response_wrapped(self):
        """A handler that returns a plain dict is wrapped in APIResponse.success."""
        api = create_api()
        router = create_router()

        @router.get("/raw")
        def raw_handler(req):
            # Return a non-APIResponse object; the framework should wrap it
            return {"wrapped": True}

        api.add_router(router)
        resp = api.handle_request("GET", "/raw")
        assert resp.status_code == HTTPStatus.OK
        assert resp.body == {"wrapped": True}

    def test_global_middleware_can_short_circuit(self):
        """A global middleware that returns a response short-circuits handler."""
        api = create_api()
        router = create_router()

        @router.get("/protected")
        def protected(req):
            return APIResponse.success({"secret": "data"})

        api.add_router(router)

        def auth_guard(req):
            if "Authorization" not in req.headers:
                return APIResponse.error("unauthorized", HTTPStatus.UNAUTHORIZED)
            return None

        api.add_middleware(auth_guard)
        resp = api.handle_request("GET", "/protected")
        assert resp.status_code == HTTPStatus.UNAUTHORIZED

    def test_global_middleware_passes_through_with_header(self):
        api = create_api()
        router = create_router()

        @router.get("/guarded")
        def guarded(req):
            return APIResponse.success({"ok": True})

        api.add_router(router)

        def auth_guard(req):
            if "Authorization" not in req.headers:
                return APIResponse.error("unauthorized", HTTPStatus.UNAUTHORIZED)
            return None

        api.add_middleware(auth_guard)
        resp = api.handle_request(
            "GET", "/guarded", headers={"Authorization": "Bearer token"}
        )
        assert resp.status_code == HTTPStatus.OK

    def test_endpoint_middleware_can_short_circuit(self):
        """Per-endpoint middleware fires before the handler."""
        api = create_api()
        router = create_router()

        def reject_all(req):
            return APIResponse.error("blocked", HTTPStatus.FORBIDDEN)

        ep = APIEndpoint(
            path="/locked",
            method=HTTPMethod.GET,
            handler=lambda req: APIResponse.success({"pass": True}),
            middleware=[reject_all],
        )
        api.router.add_endpoint(ep)
        resp = api.handle_request("GET", "/locked")
        assert resp.status_code == HTTPStatus.FORBIDDEN

    def test_add_router(self):
        api = create_api()
        router = create_router(prefix="/extra")

        @router.get("/thing")
        def handler(req):
            return APIResponse.success()

        api.add_router(router)
        resp = api.handle_request("GET", "/extra/thing")
        assert resp.status_code == HTTPStatus.OK

    def test_router_middleware_can_short_circuit(self):
        """Router-level middleware on api.router (lines 395-398) fires before handler."""
        api = create_api()
        router = create_router(prefix="/guarded")

        @router.get("/secret")
        def secret(req):
            return APIResponse.success({"secret": "data"})

        api.add_router(router)

        def main_router_guard(req):
            if req.headers.get("X-Token") != "valid":
                return APIResponse.error("forbidden", HTTPStatus.FORBIDDEN)
            return None

        # Add middleware directly to api.router (the main router) — that's what
        # self.router.middleware refers to in handle_request lines 395-398
        api.router.add_middleware(main_router_guard)

        # Without token — should be blocked by router middleware
        resp = api.handle_request("GET", "/guarded/secret")
        assert resp.status_code == HTTPStatus.FORBIDDEN

        # With token — should pass through
        resp = api.handle_request(
            "GET", "/guarded/secret", headers={"X-Token": "valid"}
        )
        assert resp.status_code == HTTPStatus.OK


# ===========================================================================
# create_router convenience function
# ===========================================================================

class TestCreateRouter:
    """create_router factory."""

    def test_creates_router_with_prefix(self):
        r = create_router(prefix="/v3")
        assert isinstance(r, APIRouter)
        assert r.prefix == "/v3"

    def test_creates_router_with_empty_prefix(self):
        r = create_router()
        assert r.prefix == ""


# ===========================================================================
# Path-to-regex conversion
# ===========================================================================

class TestPathToRegex:
    """Internal _path_to_regex — parametrized and non-parametrized paths."""

    def test_static_path_matches(self):
        router = APIRouter()
        pattern, names = router._path_to_regex("/static/path")
        assert names == []
        assert pattern.match("/static/path") is not None
        assert pattern.match("/other") is None

    def test_parametrized_path_extracts_name(self):
        router = APIRouter()
        pattern, names = router._path_to_regex("/users/{id}")
        assert "id" in names
        m = pattern.match("/users/42")
        assert m is not None
        assert m.group("id") == "42"

    def test_multiple_params_extracted(self):
        router = APIRouter()
        pattern, names = router._path_to_regex("/a/{x}/b/{y}")
        assert "x" in names
        assert "y" in names
        m = pattern.match("/a/foo/b/bar")
        assert m.group("x") == "foo"
        assert m.group("y") == "bar"
