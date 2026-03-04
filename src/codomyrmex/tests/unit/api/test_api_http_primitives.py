"""Unit tests for HTTP method and status code primitives."""

import pytest


class TestHTTPMethod:
    """Tests for HTTPMethod enum."""

    def test_all_http_methods_exist(self):
        """Test that all standard HTTP methods are defined."""
        from codomyrmex.api.standardization.rest_api import HTTPMethod

        assert HTTPMethod.GET.value == "GET"
        assert HTTPMethod.POST.value == "POST"
        assert HTTPMethod.PUT.value == "PUT"
        assert HTTPMethod.DELETE.value == "DELETE"
        assert HTTPMethod.PATCH.value == "PATCH"
        assert HTTPMethod.OPTIONS.value == "OPTIONS"
        assert HTTPMethod.HEAD.value == "HEAD"

    def test_http_method_from_string(self):
        """Test creating HTTPMethod from string."""
        from codomyrmex.api.standardization.rest_api import HTTPMethod

        assert HTTPMethod("GET") == HTTPMethod.GET
        assert HTTPMethod("POST") == HTTPMethod.POST


class TestHTTPStatus:
    """Tests for HTTPStatus enum."""

    def test_success_status_codes(self):
        """Test success status codes."""
        from codomyrmex.api.standardization.rest_api import HTTPStatus

        assert HTTPStatus.OK.value == 200
        assert HTTPStatus.CREATED.value == 201
        assert HTTPStatus.NO_CONTENT.value == 204

    def test_client_error_status_codes(self):
        """Test client error status codes."""
        from codomyrmex.api.standardization.rest_api import HTTPStatus

        assert HTTPStatus.BAD_REQUEST.value == 400
        assert HTTPStatus.UNAUTHORIZED.value == 401
        assert HTTPStatus.FORBIDDEN.value == 403
        assert HTTPStatus.NOT_FOUND.value == 404

    def test_server_error_status_codes(self):
        """Test server error status codes."""
        from codomyrmex.api.standardization.rest_api import HTTPStatus

        assert HTTPStatus.INTERNAL_SERVER_ERROR.value == 500
        assert HTTPStatus.NOT_IMPLEMENTED.value == 501
