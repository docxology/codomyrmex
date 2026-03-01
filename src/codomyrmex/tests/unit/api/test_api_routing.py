"""Unit tests for API routing and REST API handler."""

import json
import os
import tempfile
from datetime import datetime

import pytest


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
            APIRequest,
            APIResponse,
            APIRouter,
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
            APIRequest,
            APIResponse,
            APIRouter,
            HTTPMethod,
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
            APIRequest,
            APIResponse,
            APIRouter,
            HTTPMethod,
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
            RESTAPI,
            APIRequest,
            APIResponse,
        )

        api = RESTAPI()

        @api.router.get("/test")
        def test_handler(request: APIRequest) -> APIResponse:
            """Test functionality: handler."""
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
            RESTAPI,
            APIRequest,
            APIResponse,
        )

        api = RESTAPI()

        @api.router.get("/test")
        def test_handler(request: APIRequest) -> APIResponse:
            """Test functionality: handler."""
            return APIResponse.success({})

        # Make some requests
        api.handle_request("GET", "/test")
        api.handle_request("GET", "/test")

        metrics = api.get_metrics()
        assert metrics["total_requests"] == 2


class TestAPIRouterEdgeCases:
    """Additional edge case tests for APIRouter."""

    def test_router_with_nested_routers(self):
        """Test router with nested sub-routers."""
        from codomyrmex.api.standardization.rest_api import (
            APIRequest,
            APIResponse,
            APIRouter,
        )

        main_router = APIRouter(prefix="/api")
        v1_router = APIRouter(prefix="/v1")
        users_router = APIRouter(prefix="/users")

        @users_router.get("/")
        def list_users(request: APIRequest) -> APIResponse:
            return APIResponse.success([])

        v1_router.add_router(users_router)
        main_router.add_router(v1_router)

        endpoints = main_router.get_all_endpoints()
        assert len(endpoints) >= 1

    def test_router_middleware(self):
        """Test router middleware functionality."""
        from codomyrmex.api.standardization.rest_api import (
            APIRequest,
            APIRouter,
        )

        router = APIRouter()
        middleware_called = []

        def test_middleware(request: APIRequest):
            """Test functionality: middleware."""
            middleware_called.append(True)
            return None

        router.add_middleware(test_middleware)

        assert len(router.middleware) == 1

    def test_router_normalize_path(self):
        """Test path normalization."""
        from codomyrmex.api.standardization.rest_api import APIRouter

        router = APIRouter(prefix="/api")

        # Path without leading slash should be normalized
        normalized = router._normalize_path("users")
        assert normalized.startswith("/")

    def test_router_multiple_methods_same_path(self):
        """Test multiple HTTP methods on same path."""
        from codomyrmex.api.standardization.rest_api import (
            APIRequest,
            APIResponse,
            APIRouter,
        )

        router = APIRouter()

        @router.get("/items")
        def get_items(request: APIRequest) -> APIResponse:
            return APIResponse.success([])

        @router.post("/items")
        def create_item(request: APIRequest) -> APIResponse:
            return APIResponse.success({"id": 1})

        @router.delete("/items")
        def delete_items(request: APIRequest) -> APIResponse:
            return APIResponse.success({})

        endpoints = router.get_all_endpoints()
        assert len(endpoints) == 3


class TestRESTAPIEdgeCases:
    """Additional edge case tests for RESTAPI."""

    def test_api_invalid_method(self):
        """Test handling request with invalid HTTP method."""
        from codomyrmex.api.standardization.rest_api import RESTAPI

        api = RESTAPI()
        response = api.handle_request("INVALID", "/test")

        assert response.status_code.value == 405

    def test_api_options_request(self):
        """Test CORS preflight OPTIONS request."""
        from codomyrmex.api.standardization.rest_api import RESTAPI

        api = RESTAPI()
        response = api.handle_request("OPTIONS", "/any")

        assert response.status_code.value == 200
        assert "Access-Control-Allow-Origin" in response.headers

    def test_api_request_with_query_string(self):
        """Test handling request with query string."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI,
            APIRequest,
            APIResponse,
        )

        api = RESTAPI()

        @api.router.get("/search")
        def search(request: APIRequest) -> APIResponse:
            q = request.query_params.get("q", [""])[0]
            return APIResponse.success({"query": q})

        response = api.handle_request("GET", "/search", query_string="q=test")

        assert response.status_code.value == 200

    def test_api_error_in_handler(self):
        """Test error handling when handler raises exception."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI,
            APIRequest,
            APIResponse,
        )

        api = RESTAPI()

        @api.router.get("/error")
        def error_handler(request: APIRequest) -> APIResponse:
            raise ValueError("Intentional error")

        response = api.handle_request("GET", "/error")

        assert response.status_code.value == 500


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
        from codomyrmex.api.standardization.api_versioning import (
            create_versioned_endpoint,
        )

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


class TestAPIIntegration:
    """Integration tests for the API module."""

    def test_rest_api_with_router(self):
        """Test REST API with nested router."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI,
            APIRequest,
            APIResponse,
            APIRouter,
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
            APIVersion,
            APIVersionManager,
            VersionFormat,
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
        from codomyrmex.api.openapi_generator import StandardizationOpenAPIGenerator
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI,
            APIRequest,
            APIResponse,
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


class TestGraphQLAPI:
    """Tests for GraphQL API functionality."""

    def test_create_graphql_schema(self):
        """Test creating GraphQL schema."""
        from codomyrmex.api.standardization.graphql_api import (
            GraphQLField,
            GraphQLObjectType,
            GraphQLSchema,
        )

        schema = GraphQLSchema()

        user_type = GraphQLObjectType(name="User", description="User type")
        user_type.add_field(GraphQLField(name="id", type="ID", required=True))
        user_type.add_field(GraphQLField(name="name", type="String"))

        schema.add_type(user_type)

        assert schema.get_type("User") is not None
        assert "id" in schema.get_type("User").fields

    def test_graphql_schema_sdl_generation(self):
        """Test SDL generation from GraphQL schema."""
        from codomyrmex.api.standardization.graphql_api import (
            GraphQLField,
            GraphQLObjectType,
            GraphQLSchema,
        )

        schema = GraphQLSchema()

        user_type = GraphQLObjectType(name="User")
        user_type.add_field(GraphQLField(name="id", type="ID", required=True))

        query_type = GraphQLObjectType(name="Query")
        query_type.add_field(GraphQLField(name="user", type="User"))

        schema.add_type(user_type)
        schema.query_type = query_type

        sdl = schema.generate_sdl()

        assert "type User" in sdl
        assert "type Query" in sdl

    def test_graphql_api_metrics(self):
        """Test GraphQL API metrics."""
        from codomyrmex.api.standardization.graphql_api import GraphQLAPI, GraphQLSchema

        schema = GraphQLSchema()
        api = GraphQLAPI(schema)

        # Execute some queries
        api.execute_query("{ test }")
        api.execute_query("{ test }")

        metrics = api.get_metrics()

        assert "total_requests" in metrics
        assert metrics["total_requests"] == 2

    def test_graphql_mutation_execution(self):
        """Test GraphQL mutation execution."""
        from codomyrmex.api.standardization.graphql_api import (
            GraphQLField,
            GraphQLMutation,
            GraphQLObjectType,
        )

        input_type = GraphQLObjectType(name="CreateUserInput")
        input_type.add_field(GraphQLField(name="name", type="String", required=True))

        def create_user_resolver(input_data, context):
            return {"id": "1", "name": input_data.get("name")}

        mutation = GraphQLMutation(
            name="createUser",
            input_type=input_type,
            output_type="User",
            resolver=create_user_resolver,
            description="Create a new user"
        )

        result = mutation.execute({"name": "Test User"}, {})

        assert result["id"] == "1"
        assert result["name"] == "Test User"

    def test_graphql_resolver_decorator(self):
        """Test GraphQL resolver decorator."""
        from codomyrmex.api.standardization.graphql_api import resolver

        @resolver("users", complexity=5)
        def get_users(parent, args, context):
            return []

        assert get_users.field_name == "users"
        assert get_users.complexity == 5


class TestModuleImports:
    """Tests for module-level imports and exports."""

    def test_api_module_imports(self):
        """Test that main API module exports are accessible."""
        from codomyrmex.api import (
            RESTAPI,
            APIResponse,
            APIVersionManager,
            GraphQLSchema,
        )

        assert RESTAPI is not None
        assert APIResponse is not None
        assert GraphQLSchema is not None
        assert APIVersionManager is not None

    def test_standardization_module_imports(self):
        """Test standardization submodule imports."""
        from codomyrmex.api.standardization import (
            create_api,
            create_router,
            create_schema,
            create_version_manager,
        )

        assert create_api is not None
        assert create_router is not None
        assert create_schema is not None
        assert create_version_manager is not None

    def test_documentation_module_imports(self):
        """Test documentation submodule imports."""
        from codomyrmex.api.documentation import (
            APIDocumentation,
            APIDocumentationGenerator,
            generate_api_docs,
        )

        assert APIDocumentationGenerator is not None
        assert generate_api_docs is not None
        assert APIDocumentation is not None


# Mark slow tests
@pytest.mark.slow
class TestAPIPerformance:
    """Performance-related tests for API module."""

    def test_router_many_endpoints(self):
        """Test router with many endpoints."""
        from codomyrmex.api.standardization.rest_api import (
            APIRequest,
            APIResponse,
            APIRouter,
        )

        router = APIRouter()

        # Add 100 endpoints
        for i in range(100):
            @router.get(f"/endpoint_{i}")
            def handler(request: APIRequest, idx=i) -> APIResponse:
                return APIResponse.success({"endpoint": idx})

        endpoints = router.get_all_endpoints()
        assert len(endpoints) == 100

    def test_api_multiple_requests(self):
        """Test handling multiple requests."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI,
            APIRequest,
            APIResponse,
        )

        api = RESTAPI()

        @api.router.get("/test")
        def handler(request: APIRequest) -> APIResponse:
            return APIResponse.success({})

        # Make 50 requests
        for _ in range(50):
            response = api.handle_request("GET", "/test")
            assert response.status_code.value == 200

        metrics = api.get_metrics()
        assert metrics["total_requests"] == 50
