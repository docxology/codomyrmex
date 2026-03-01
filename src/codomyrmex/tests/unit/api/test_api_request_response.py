"""Unit tests for API request and response data models."""

import json

import pytest


class TestAPIRequest:
    """Tests for APIRequest dataclass."""

    def test_create_request(self):
        """Test creating a basic API request."""
        from codomyrmex.api.standardization.rest_api import APIRequest, HTTPMethod

        request = APIRequest(
            method=HTTPMethod.GET,
            path="/users"
        )

        assert request.method == HTTPMethod.GET
        assert request.path == "/users"
        assert request.headers == {}
        assert request.query_params == {}
        assert request.body is None

    def test_request_with_headers(self):
        """Test request with headers."""
        from codomyrmex.api.standardization.rest_api import APIRequest, HTTPMethod

        headers = {"Authorization": "Bearer token123"}
        request = APIRequest(
            method=HTTPMethod.GET,
            path="/users",
            headers=headers
        )

        assert request.headers["Authorization"] == "Bearer token123"

    def test_json_body_parsing(self):
        """Test JSON body parsing."""
        from codomyrmex.api.standardization.rest_api import APIRequest, HTTPMethod

        body = json.dumps({"name": "test"}).encode('utf-8')
        request = APIRequest(
            method=HTTPMethod.POST,
            path="/users",
            body=body
        )

        assert request.json_body == {"name": "test"}

    def test_json_body_invalid(self):
        """Test invalid JSON body returns None."""
        from codomyrmex.api.standardization.rest_api import APIRequest, HTTPMethod

        body = b"not valid json"
        request = APIRequest(
            method=HTTPMethod.POST,
            path="/users",
            body=body
        )

        assert request.json_body is None


class TestAPIResponse:
    """Tests for APIResponse dataclass."""

    def test_create_response(self):
        """Test creating a basic API response."""
        from codomyrmex.api.standardization.rest_api import APIResponse, HTTPStatus

        response = APIResponse(status_code=HTTPStatus.OK)

        assert response.status_code == HTTPStatus.OK
        assert "Content-Type" in response.headers

    def test_success_response(self):
        """Test creating success response."""
        from codomyrmex.api.standardization.rest_api import APIResponse, HTTPStatus

        response = APIResponse.success({"id": 1})

        assert response.status_code == HTTPStatus.OK
        assert response.body == {"id": 1}

    def test_error_response(self):
        """Test creating error response."""
        from codomyrmex.api.standardization.rest_api import APIResponse, HTTPStatus

        response = APIResponse.error("Something went wrong")

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "error" in response.body

    def test_not_found_response(self):
        """Test creating not found response."""
        from codomyrmex.api.standardization.rest_api import APIResponse, HTTPStatus

        response = APIResponse.not_found("User")

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in response.body["error"]

    def test_bad_request_response(self):
        """Test creating bad request response."""
        from codomyrmex.api.standardization.rest_api import APIResponse, HTTPStatus

        response = APIResponse.bad_request("Invalid input")

        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestAPIRequestEdgeCases:
    """Additional edge case tests for APIRequest."""

    def test_request_with_empty_body(self):
        """Test request with empty body."""
        from codomyrmex.api.standardization.rest_api import APIRequest, HTTPMethod

        request = APIRequest(
            method=HTTPMethod.POST,
            path="/test",
            body=b""
        )

        assert request.json_body is None

    def test_request_with_unicode_body(self):
        """Test request with unicode content in body."""
        from codomyrmex.api.standardization.rest_api import APIRequest, HTTPMethod

        body = json.dumps({"name": "Test User", "emoji": "Hello World"}).encode('utf-8')
        request = APIRequest(
            method=HTTPMethod.POST,
            path="/users",
            body=body
        )

        assert request.json_body is not None
        assert request.json_body["name"] == "Test User"

    def test_request_with_nested_query_params(self):
        """Test request with multiple query parameter values."""
        from codomyrmex.api.standardization.rest_api import APIRequest, HTTPMethod

        request = APIRequest(
            method=HTTPMethod.GET,
            path="/search",
            query_params={"tags": ["python", "api", "rest"]}
        )

        assert len(request.query_params["tags"]) == 3

    def test_request_context_usage(self):
        """Test request context dictionary."""
        from codomyrmex.api.standardization.rest_api import APIRequest, HTTPMethod

        request = APIRequest(
            method=HTTPMethod.GET,
            path="/test",
            context={"user_id": 123, "session": "abc"}
        )

        assert request.context["user_id"] == 123
        assert request.context["session"] == "abc"


class TestAPIResponseEdgeCases:
    """Additional edge case tests for APIResponse."""

    def test_response_with_custom_headers(self):
        """Test response with custom headers."""
        from codomyrmex.api.standardization.rest_api import APIResponse, HTTPStatus

        response = APIResponse(
            status_code=HTTPStatus.OK,
            body={"data": "test"},
            headers={"X-Custom-Header": "custom-value"}
        )

        assert "X-Custom-Header" in response.headers
        assert response.headers["X-Custom-Header"] == "custom-value"

    def test_response_with_custom_content_type(self):
        """Test response with custom content type."""
        from codomyrmex.api.standardization.rest_api import APIResponse, HTTPStatus

        response = APIResponse(
            status_code=HTTPStatus.OK,
            body="<html></html>",
            content_type="text/html"
        )

        assert response.content_type == "text/html"

    def test_response_success_with_custom_status(self):
        """Test success response with custom status code."""
        from codomyrmex.api.standardization.rest_api import APIResponse, HTTPStatus

        response = APIResponse.success({"id": 1}, status_code=HTTPStatus.CREATED)

        assert response.status_code == HTTPStatus.CREATED

    def test_response_error_with_custom_status(self):
        """Test error response with custom status code."""
        from codomyrmex.api.standardization.rest_api import APIResponse, HTTPStatus

        response = APIResponse.error("Forbidden", HTTPStatus.FORBIDDEN)

        assert response.status_code == HTTPStatus.FORBIDDEN
