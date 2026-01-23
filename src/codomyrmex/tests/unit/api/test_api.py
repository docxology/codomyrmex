"""Tests for the Codomyrmex API module.

This module tests REST API, API versioning, and OpenAPI generation functionality.
"""

import json
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


# REST API Tests
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


class TestAPIRouter:
    """Tests for APIRouter class."""

    def test_create_router(self):
        """Test creating a router."""
        from codomyrmex.api.standardization.rest_api import APIRouter

        router = APIRouter(prefix="/api")

        assert router.prefix == "/api"
        assert router.endpoints == {}

    def test_add_endpoint_via_decorator(self):
        """Test adding endpoint via decorator."""
        from codomyrmex.api.standardization.rest_api import (
            APIRouter, APIRequest, APIResponse, HTTPStatus
        )

        router = APIRouter()

        @router.get("/users", summary="Get all users")
        def get_users(request: APIRequest) -> APIResponse:
            return APIResponse.success([])

        endpoints = router.get_all_endpoints()
        assert len(endpoints) == 1
        assert endpoints[0].path == "/users"

    def test_match_endpoint(self):
        """Test matching an endpoint."""
        from codomyrmex.api.standardization.rest_api import (
            APIRouter, APIRequest, APIResponse, HTTPMethod
        )

        router = APIRouter()

        @router.get("/users")
        def get_users(request: APIRequest) -> APIResponse:
            return APIResponse.success([])

        match = router.match_endpoint(HTTPMethod.GET, "/users")
        assert match is not None
        endpoint, params = match
        assert endpoint.path == "/users"

    def test_match_endpoint_with_params(self):
        """Test matching an endpoint with path parameters."""
        from codomyrmex.api.standardization.rest_api import (
            APIRouter, APIRequest, APIResponse, HTTPMethod
        )

        router = APIRouter()

        @router.get("/users/{id}")
        def get_user(request: APIRequest) -> APIResponse:
            return APIResponse.success({})

        match = router.match_endpoint(HTTPMethod.GET, "/users/123")
        assert match is not None
        endpoint, params = match
        assert params["id"] == "123"


class TestRESTAPI:
    """Tests for RESTAPI class."""

    def test_create_api(self):
        """Test creating a REST API."""
        from codomyrmex.api.standardization.rest_api import RESTAPI

        api = RESTAPI(title="Test API", version="1.0.0")

        assert api.title == "Test API"
        assert api.version == "1.0.0"

    def test_handle_request(self):
        """Test handling a request."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI, APIRequest, APIResponse
        )

        api = RESTAPI()

        @api.router.get("/test")
        def test_handler(request: APIRequest) -> APIResponse:
            return APIResponse.success({"message": "OK"})

        response = api.handle_request("GET", "/test")

        assert response.status_code.value == 200
        assert response.body == {"message": "OK"}

    def test_handle_not_found(self):
        """Test handling request to non-existent endpoint."""
        from codomyrmex.api.standardization.rest_api import RESTAPI

        api = RESTAPI()
        response = api.handle_request("GET", "/nonexistent")

        assert response.status_code.value == 404

    def test_metrics(self):
        """Test API metrics."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI, APIRequest, APIResponse
        )

        api = RESTAPI()

        @api.router.get("/test")
        def test_handler(request: APIRequest) -> APIResponse:
            return APIResponse.success({})

        # Make some requests
        api.handle_request("GET", "/test")
        api.handle_request("GET", "/test")

        metrics = api.get_metrics()
        assert metrics["total_requests"] == 2


# API Versioning Tests
class TestSimpleVersion:
    """Tests for SimpleVersion class."""

    def test_parse_valid_version(self):
        """Test parsing a valid semantic version."""
        from codomyrmex.api.standardization.api_versioning import SimpleVersion

        version = SimpleVersion("1.2.3")

        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_parse_invalid_version(self):
        """Test parsing an invalid version raises error."""
        from codomyrmex.api.standardization.api_versioning import SimpleVersion

        with pytest.raises(ValueError):
            SimpleVersion("invalid")

    def test_version_comparison(self):
        """Test version comparison."""
        from codomyrmex.api.standardization.api_versioning import SimpleVersion

        v1 = SimpleVersion("1.0.0")
        v2 = SimpleVersion("2.0.0")
        v3 = SimpleVersion("1.1.0")

        assert v1 < v2
        assert v1 < v3
        assert v3 < v2

    def test_version_equality(self):
        """Test version equality."""
        from codomyrmex.api.standardization.api_versioning import SimpleVersion

        v1 = SimpleVersion("1.0.0")
        v2 = SimpleVersion("1.0.0")

        assert v1 == v2

    def test_version_compatibility(self):
        """Test version compatibility check."""
        from codomyrmex.api.standardization.api_versioning import SimpleVersion

        v1 = SimpleVersion("1.0.0")
        v2 = SimpleVersion("1.5.0")
        v3 = SimpleVersion("2.0.0")

        assert v1.is_compatible(v2)
        assert not v1.is_compatible(v3)


class TestAPIVersion:
    """Tests for APIVersion dataclass."""

    def test_create_semver_version(self):
        """Test creating a semantic version."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion, VersionFormat
        )

        version = APIVersion(
            version="1.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now(),
            description="Initial release"
        )

        assert version.version == "1.0.0"
        assert version.format == VersionFormat.SEMVER

    def test_create_date_version(self):
        """Test creating a date-based version."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion, VersionFormat
        )

        version = APIVersion(
            version="2024-01-01",
            format=VersionFormat.DATE,
            release_date=datetime.now()
        )

        assert version.version == "2024-01-01"

    def test_create_integer_version(self):
        """Test creating an integer version."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion, VersionFormat
        )

        version = APIVersion(
            version="1",
            format=VersionFormat.INTEGER,
            release_date=datetime.now()
        )

        assert version.version == "1"

    def test_invalid_semver_format(self):
        """Test that invalid semver raises error."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion, VersionFormat
        )

        with pytest.raises(ValueError):
            APIVersion(
                version="invalid",
                format=VersionFormat.SEMVER,
                release_date=datetime.now()
            )

    def test_version_compatibility(self):
        """Test version compatibility checking."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion, VersionFormat
        )

        v1 = APIVersion(
            version="1.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now()
        )
        v2 = APIVersion(
            version="1.5.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now()
        )

        assert v1.is_compatible_with(v2)


class TestAPIVersionManager:
    """Tests for APIVersionManager class."""

    def test_create_version_manager(self):
        """Test creating a version manager."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        assert manager.default_version == "1.0.0"
        assert "1.0.0" in manager.versions

    def test_register_version(self):
        """Test registering a new version."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersionManager, APIVersion, VersionFormat
        )

        manager = APIVersionManager()

        new_version = APIVersion(
            version="2.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now(),
            description="Major update"
        )

        manager.register_version(new_version)

        assert "2.0.0" in manager.versions

    def test_validate_version(self):
        """Test version validation."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        assert manager.validate_version("1.0.0")
        assert not manager.validate_version("9.9.9")

    def test_get_supported_versions(self):
        """Test getting supported versions."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersionManager, APIVersion, VersionFormat
        )

        manager = APIVersionManager(default_version="1.0.0")
        manager.register_version(APIVersion(
            version="2.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now()
        ))

        versions = manager.get_supported_versions()

        assert len(versions) == 2

    def test_parse_version_from_request_header(self):
        """Test parsing version from request header."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        headers = {"x-api-version": "2.0.0"}
        query_params = {}

        version = manager.parse_version_from_request(headers, query_params)

        assert version == "2.0.0"

    def test_parse_version_from_query_param(self):
        """Test parsing version from query parameter."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        headers = {}
        query_params = {"version": ["2.0.0"]}

        version = manager.parse_version_from_request(headers, query_params)

        assert version == "2.0.0"

    def test_get_version_info(self):
        """Test getting version information."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        info = manager.get_version_info()

        assert "default_version" in info
        assert "supported_versions" in info
        assert info["default_version"] == "1.0.0"


class TestVersionedEndpoint:
    """Tests for VersionedEndpoint dataclass."""

    def test_create_versioned_endpoint(self):
        """Test creating a versioned endpoint."""
        from codomyrmex.api.standardization.api_versioning import VersionedEndpoint

        def handler_v1():
            return "v1"

        endpoint = VersionedEndpoint(
            path="/users",
            versions={"1.0.0": handler_v1},
            default_version="1.0.0"
        )

        assert endpoint.path == "/users"
        assert "1.0.0" in endpoint.versions

    def test_get_handler_for_version(self):
        """Test getting handler for specific version."""
        from codomyrmex.api.standardization.api_versioning import VersionedEndpoint

        def handler_v1():
            return "v1"

        def handler_v2():
            return "v2"

        endpoint = VersionedEndpoint(
            path="/users",
            versions={"1.0.0": handler_v1, "2.0.0": handler_v2},
            default_version="1.0.0"
        )

        assert endpoint.get_handler("2.0.0")() == "v2"

    def test_add_version(self):
        """Test adding a new version to endpoint."""
        from codomyrmex.api.standardization.api_versioning import VersionedEndpoint

        def handler_v1():
            return "v1"

        def handler_v2():
            return "v2"

        endpoint = VersionedEndpoint(
            path="/users",
            versions={"1.0.0": handler_v1},
            default_version="1.0.0"
        )

        endpoint.add_version("2.0.0", handler_v2)

        assert "2.0.0" in endpoint.versions


# OpenAPI Generator Tests
class TestAPISchema:
    """Tests for APISchema dataclass."""

    def test_create_schema(self):
        """Test creating an API schema."""
        from codomyrmex.api.openapi_generator import APISchema

        schema = APISchema(
            name="User",
            schema_type="object",
            properties={
                "id": {"type": "integer"},
                "name": {"type": "string"}
            },
            required=["id", "name"]
        )

        assert schema.name == "User"
        assert schema.schema_type == "object"

    def test_schema_to_dict(self):
        """Test converting schema to dictionary."""
        from codomyrmex.api.openapi_generator import APISchema

        schema = APISchema(
            name="User",
            schema_type="object",
            properties={"id": {"type": "integer"}},
            required=["id"]
        )

        result = schema.to_dict()

        assert result["type"] == "object"
        assert "properties" in result
        assert "required" in result


class TestOpenAPISpecification:
    """Tests for OpenAPISpecification class."""

    def test_create_specification(self):
        """Test creating an OpenAPI specification."""
        from codomyrmex.api.openapi_generator import OpenAPISpecification

        spec = OpenAPISpecification()
        spec.spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {}
        }

        assert spec.version == "3.0.3"

    def test_specification_to_json(self):
        """Test converting specification to JSON."""
        from codomyrmex.api.openapi_generator import OpenAPISpecification

        spec = OpenAPISpecification()
        spec.spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {}
        }

        json_str = spec.to_json()

        assert "openapi" in json_str
        assert "3.0.3" in json_str

    def test_specification_to_yaml(self):
        """Test converting specification to YAML."""
        from codomyrmex.api.openapi_generator import OpenAPISpecification

        spec = OpenAPISpecification()
        spec.spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {}
        }

        yaml_str = spec.to_yaml()

        assert "openapi" in yaml_str

    def test_save_to_file(self):
        """Test saving specification to file."""
        from codomyrmex.api.openapi_generator import OpenAPISpecification

        spec = OpenAPISpecification()
        spec.spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            spec.save_to_file(filepath, format="json")

            with open(filepath) as f:
                loaded = json.load(f)

            assert loaded["openapi"] == "3.0.3"
        finally:
            os.unlink(filepath)


class TestDocumentationOpenAPIGenerator:
    """Tests for DocumentationOpenAPIGenerator class."""

    def test_generate_spec(self):
        """Test generating OpenAPI specification."""
        from codomyrmex.api.openapi_generator import DocumentationOpenAPIGenerator

        generator = DocumentationOpenAPIGenerator()

        endpoints = [
            {
                "path": "/users",
                "method": "GET",
                "summary": "Get all users",
                "description": "Returns a list of users"
            }
        ]

        spec = generator.generate_spec(
            title="Test API",
            version="1.0.0",
            endpoints=endpoints
        )

        assert spec["openapi"] == "3.0.3"
        assert spec["info"]["title"] == "Test API"
        assert "/users" in spec["paths"]

    def test_validate_spec_valid(self):
        """Test validating a valid specification."""
        from codomyrmex.api.openapi_generator import DocumentationOpenAPIGenerator

        generator = DocumentationOpenAPIGenerator()

        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        errors = generator.validate_spec(spec)

        assert len(errors) == 0

    def test_validate_spec_missing_fields(self):
        """Test validating specification with missing fields."""
        from codomyrmex.api.openapi_generator import DocumentationOpenAPIGenerator

        generator = DocumentationOpenAPIGenerator()

        spec = {"paths": {}}

        errors = generator.validate_spec(spec)

        assert len(errors) > 0
        assert any("openapi" in e for e in errors)

    def test_get_default_schemas(self):
        """Test getting default schemas."""
        from codomyrmex.api.openapi_generator import DocumentationOpenAPIGenerator

        generator = DocumentationOpenAPIGenerator()

        schemas = generator._get_default_schemas()

        assert "Error" in schemas
        assert "Success" in schemas

    def test_get_default_security_schemes(self):
        """Test getting default security schemes."""
        from codomyrmex.api.openapi_generator import DocumentationOpenAPIGenerator

        generator = DocumentationOpenAPIGenerator()

        schemes = generator._get_default_security_schemes()

        assert "BearerAuth" in schemes
        assert "ApiKeyAuth" in schemes

    def test_export_spec_json(self):
        """Test exporting specification to JSON file."""
        from codomyrmex.api.openapi_generator import DocumentationOpenAPIGenerator

        generator = DocumentationOpenAPIGenerator()
        spec = generator.generate_spec("Test API", "1.0.0", [])

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "spec.json")
            result = generator.export_spec(spec, filepath, format="json")

            assert result is True
            assert os.path.exists(filepath)


class TestStandardizationOpenAPIGenerator:
    """Tests for StandardizationOpenAPIGenerator class."""

    def test_create_generator(self):
        """Test creating a standardization OpenAPI generator."""
        from codomyrmex.api.openapi_generator import StandardizationOpenAPIGenerator

        generator = StandardizationOpenAPIGenerator(
            title="Test API",
            version="1.0.0",
            description="Test description"
        )

        assert generator.title == "Test API"
        assert generator.version == "1.0.0"

    def test_add_security_schemes(self):
        """Test adding security schemes."""
        from codomyrmex.api.openapi_generator import StandardizationOpenAPIGenerator

        generator = StandardizationOpenAPIGenerator()

        generator.add_security_schemes({
            "CustomAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-Custom-Key"
            }
        })

        assert "CustomAuth" in generator.spec.spec["components"]["securitySchemes"]

    def test_add_tags(self):
        """Test adding tags."""
        from codomyrmex.api.openapi_generator import StandardizationOpenAPIGenerator

        generator = StandardizationOpenAPIGenerator()

        generator.add_tags([
            {"name": "users", "description": "User operations"}
        ])

        assert len(generator.spec.spec["tags"]) > 0

    def test_set_external_docs(self):
        """Test setting external documentation."""
        from codomyrmex.api.openapi_generator import StandardizationOpenAPIGenerator

        generator = StandardizationOpenAPIGenerator()

        generator.set_external_docs("https://docs.example.com", "API Documentation")

        assert "externalDocs" in generator.spec.spec
        assert generator.spec.spec["externalDocs"]["url"] == "https://docs.example.com"

    def test_validate_spec(self):
        """Test spec validation."""
        from codomyrmex.api.openapi_generator import StandardizationOpenAPIGenerator

        generator = StandardizationOpenAPIGenerator()

        errors = generator.validate_spec()

        # Should have no errors for a freshly initialized generator
        assert isinstance(errors, list)

    def test_generate_spec(self):
        """Test generating final specification."""
        from codomyrmex.api.openapi_generator import StandardizationOpenAPIGenerator

        generator = StandardizationOpenAPIGenerator(
            title="Final API",
            version="2.0.0"
        )

        spec = generator.generate_spec()

        assert "x-generated-at" in spec.spec["info"]
        assert spec.spec["info"]["title"] == "Final API"


# Convenience Functions Tests
class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_create_api_function(self):
        """Test create_api convenience function."""
        from codomyrmex.api.standardization.rest_api import create_api

        api = create_api(title="My API", version="2.0.0")

        assert api.title == "My API"
        assert api.version == "2.0.0"

    def test_create_router_function(self):
        """Test create_router convenience function."""
        from codomyrmex.api.standardization.rest_api import create_router

        router = create_router(prefix="/v1")

        assert router.prefix == "/v1"

    def test_create_version_manager_function(self):
        """Test create_version_manager convenience function."""
        from codomyrmex.api.standardization.api_versioning import create_version_manager

        manager = create_version_manager(default_version="2.0.0")

        assert manager.default_version == "2.0.0"

    def test_create_versioned_endpoint_function(self):
        """Test create_versioned_endpoint convenience function."""
        from codomyrmex.api.standardization.api_versioning import create_versioned_endpoint

        endpoint = create_versioned_endpoint("/api/users", "1.0.0")

        assert endpoint.path == "/api/users"
        assert endpoint.default_version == "1.0.0"

    def test_generate_openapi_spec_function(self):
        """Test generate_openapi_spec convenience function."""
        from codomyrmex.api.openapi_generator import generate_openapi_spec

        spec = generate_openapi_spec(
            title="Quick API",
            version="1.0.0",
            endpoints=[]
        )

        assert spec["info"]["title"] == "Quick API"

    def test_validate_openapi_spec_function(self):
        """Test validate_openapi_spec convenience function."""
        from codomyrmex.api.openapi_generator import validate_openapi_spec

        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {}
        }

        errors = validate_openapi_spec(spec)

        assert len(errors) == 0


# Integration Tests
class TestAPIIntegration:
    """Integration tests for the API module."""

    def test_rest_api_with_router(self):
        """Test REST API with nested router."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI, APIRouter, APIRequest, APIResponse
        )

        api = RESTAPI(title="Integration Test API")

        users_router = APIRouter(prefix="/users")

        @users_router.get("/")
        def list_users(request: APIRequest) -> APIResponse:
            return APIResponse.success([{"id": 1, "name": "Test"}])

        @users_router.get("/{id}")
        def get_user(request: APIRequest) -> APIResponse:
            user_id = request.path_params.get("id")
            return APIResponse.success({"id": user_id})

        api.add_router(users_router)

        # Test list users
        response = api.handle_request("GET", "/users/")
        assert response.status_code.value == 200

        # Test get user
        response = api.handle_request("GET", "/users/123")
        assert response.status_code.value == 200

    def test_api_with_version_manager(self):
        """Test API with version management."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersionManager, APIVersion, VersionFormat
        )

        manager = APIVersionManager(default_version="1.0.0")

        # Register multiple versions
        manager.register_version(APIVersion(
            version="1.1.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now(),
            features=["New feature A"]
        ))

        manager.register_version(APIVersion(
            version="2.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now(),
            breaking_changes=["Changed endpoint format"]
        ))

        # Get version info
        info = manager.get_version_info()

        assert len(info["supported_versions"]) == 3
        assert "1.0.0" in info["supported_versions"]
        assert "2.0.0" in info["supported_versions"]

    def test_full_openapi_generation_workflow(self):
        """Test complete OpenAPI generation workflow."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI, APIRequest, APIResponse
        )
        from codomyrmex.api.openapi_generator import (
            StandardizationOpenAPIGenerator
        )

        # Create API
        api = RESTAPI(title="Full Test API", version="1.0.0")

        @api.router.get("/health")
        def health_check(request: APIRequest) -> APIResponse:
            return APIResponse.success({"status": "healthy"})

        @api.router.post("/data")
        def create_data(request: APIRequest) -> APIResponse:
            return APIResponse.success({"id": 1})

        # Generate OpenAPI spec
        generator = StandardizationOpenAPIGenerator(
            title=api.title,
            version=api.version,
            description="Full workflow test API"
        )

        # Add security schemes
        generator.add_security_schemes({
            "BearerAuth": {"type": "http", "scheme": "bearer"}
        })

        # Add tags
        generator.add_tags([
            {"name": "health", "description": "Health checks"},
            {"name": "data", "description": "Data operations"}
        ])

        # Generate spec
        spec = generator.generate_spec()

        # Validate
        errors = generator.validate_spec()
        assert len(errors) == 0

        # Check spec contents
        assert spec.spec["info"]["title"] == "Full Test API"
        assert "securitySchemes" in spec.spec["components"]
