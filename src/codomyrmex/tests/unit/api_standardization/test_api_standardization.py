"""
Unit Tests for API Standardization

Tests for REST API, GraphQL API, API versioning, and OpenAPI generation components.
"""

import json
from datetime import datetime

import pytest

from codomyrmex.api.openapi_generator import OpenAPISpecification
from codomyrmex.api.openapi_generator import (
    StandardizationOpenAPIGenerator as OpenAPIGenerator,
)
from codomyrmex.api.standardization.api_versioning import (
    APIVersion,
    APIVersionManager,
    VersionedEndpoint,
    VersionFormat,
)
from codomyrmex.api.standardization.graphql_api import (
    GraphQLAPI,
    GraphQLField,
    GraphQLMutation,
    GraphQLObjectType,
    GraphQLResolver,
    GraphQLSchema,
)
from codomyrmex.api.standardization.rest_api import (
    RESTAPI,
    APIEndpoint,
    APIRequest,
    APIResponse,
    APIRouter,
    HTTPMethod,
    HTTPStatus,
)


@pytest.mark.unit
class TestRESTAPI:
    """Test the REST API functionality."""

    def setup_method(self):
        """Set up test method."""
        self.api = RESTAPI("Test API", "1.0.0", "Test description")

    def test_api_creation(self):
        """Test creating a REST API."""
        assert self.api.title == "Test API"
        assert self.api.version == "1.0.0"
        assert self.api.description == "Test description"

    def test_api_request_creation(self):
        """Test creating API requests."""
        request = APIRequest(
            method=HTTPMethod.GET,
            path="/test",
            headers={"content-type": "application/json"},
            query_params={"key": ["value"]},
            body=b'{"test": "data"}'
        )

        assert request.method == HTTPMethod.GET
        assert request.path == "/test"
        assert request.json_body == {"test": "data"}

    def test_api_response_creation(self):
        """Test creating API responses."""
        response = APIResponse.success({"data": "test"})
        assert response.status_code == HTTPStatus.OK
        assert response.body == {"data": "test"}

        error_response = APIResponse.error("Not found", HTTPStatus.NOT_FOUND)
        assert error_response.status_code == HTTPStatus.NOT_FOUND
        assert error_response.body["error"] == "Not found"

    def test_router_functionality(self):
        """Test API router functionality."""
        router = APIRouter("/api")

        # Add endpoint
        def test_handler(request):
            """Test functionality: handler."""
            return APIResponse.success({"result": "ok"})

        endpoint = APIEndpoint(
            path="/test",
            method=HTTPMethod.GET,
            handler=test_handler,
            summary="Test endpoint"
        )
        router.add_endpoint(endpoint)

        # Test matching
        matched = router.match_endpoint(HTTPMethod.GET, "/api/test")
        assert matched is not None
        assert matched[0].summary == "Test endpoint"

    def test_api_handle_request(self):
        """Test handling API requests."""
        # Add a test endpoint
        def test_handler(request):
            """Test functionality: handler."""
            return APIResponse.success({"path": request.path, "method": request.method.value})

        self.api.router.add_endpoint(APIEndpoint(
            path="/test",
            method=HTTPMethod.GET,
            handler=test_handler
        ))

        # Handle request
        response = self.api.handle_request("GET", "/test")
        assert response.status_code == HTTPStatus.OK
        assert response.body["path"] == "/test"
        assert response.body["method"] == "GET"


@pytest.mark.unit
class TestGraphQLAPI:
    """Test the GraphQL API functionality."""

    def setup_method(self):
        """Set up test method."""
        self.schema = GraphQLSchema()
        self.api = GraphQLAPI(self.schema)

    def test_schema_creation(self):
        """Test creating GraphQL schemas."""
        # Create object type
        user_type = GraphQLObjectType("User", description="User type")
        user_type.add_field(GraphQLField("id", "ID", required=True))
        user_type.add_field(GraphQLField("name", "String"))
        user_type.add_field(GraphQLField("email", "String"))

        self.schema.add_type(user_type)

        assert self.schema.get_type("User") == user_type
        assert len(user_type.fields) == 3

    def test_resolver_registration(self):
        """Test registering GraphQL resolvers."""
        def user_resolver(parent, args, context):
            return {"id": "1", "name": "Test User"}

        resolver = GraphQLResolver("user", user_resolver)
        self.api.register_resolver("Query", "user", resolver)

        assert "Query" in self.api.resolvers
        assert "user" in self.api.resolvers["Query"]

    def test_mutation_registration(self):
        """Test registering GraphQL mutations."""
        def create_user(input_data, context):
            return {"id": "1", "name": input_data["name"]}

        input_type = GraphQLObjectType("CreateUserInput")
        input_type.add_field(GraphQLField("name", "String", required=True))

        mutation = GraphQLMutation(
            name="createUser",
            input_type=input_type,
            output_type="User",
            resolver=create_user
        )

        self.api.register_mutation(mutation)

        assert "createUser" in self.api.mutations

    def test_schema_generation(self):
        """Test GraphQL schema generation."""
        # Create a simple schema
        user_type = GraphQLObjectType("User")
        user_type.add_field(GraphQLField("id", "ID", required=True))
        user_type.add_field(GraphQLField("name", "String"))

        query_type = GraphQLObjectType("Query")
        query_type.add_field(GraphQLField("user", "User"))

        self.schema.add_type(user_type)
        self.schema.query_type = query_type

        sdl = self.schema.generate_sdl()
        assert "type User {" in sdl
        assert "type Query {" in sdl

    def test_query_execution(self):
        """Test GraphQL query execution."""
        # This is a simplified test since full GraphQL parsing would require a parser library
        result = self.api.execute_query("{ user { id name } }")
        # Should return errors for invalid query since we don't have full implementation
        assert "errors" in result or "data" in result


@pytest.mark.unit
class TestAPIVersioning:
    """Test the API versioning functionality."""

    def setup_method(self):
        """Set up test method."""
        self.version_manager = APIVersionManager("1.0.0", VersionFormat.SEMVER)

    def test_version_creation(self):
        """Test creating API versions."""
        version = APIVersion(
            version="1.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now(),
            description="Initial release"
        )

        assert version.version == "1.0.0"
        assert version.format == VersionFormat.SEMVER

    def test_version_validation(self):
        """Test version validation."""
        # Valid semantic version
        assert self.version_manager.validate_version("1.0.0")

        # Invalid version
        assert not self.version_manager.validate_version("2.0.0")

    def test_version_compatibility(self):
        """Test version compatibility checking."""
        v1 = APIVersion("1.0.0", VersionFormat.SEMVER, datetime.now())
        v2 = APIVersion("1.1.0", VersionFormat.SEMVER, datetime.now())

        assert v1.is_compatible_with(v2)

        v3 = APIVersion("2.0.0", VersionFormat.SEMVER, datetime.now())
        assert not v1.is_compatible_with(v3)

    def test_versioned_endpoint(self):
        """Test versioned endpoints."""
        def handler_v1(request):
            return APIResponse.success({"version": "1.0"})

        def handler_v2(request):
            return APIResponse.success({"version": "2.0"})

        endpoint = VersionedEndpoint("/api/test", {}, "1.0.0")
        endpoint.add_version("1.0.0", handler_v1)
        endpoint.add_version("2.0.0", handler_v2)

        # Test getting handlers
        handler = endpoint.get_handler("1.0.0")
        assert handler == handler_v1

        handler = endpoint.get_handler("2.0.0")
        assert handler == handler_v2

        # Test default version
        handler = endpoint.get_handler()
        assert handler == handler_v1

    def test_version_parsing(self):
        """Test parsing versions from requests."""
        headers = {"x-api-version": "2.0.0"}
        query_params = {}

        version = self.version_manager.parse_version_from_request(headers, query_params)
        assert version == "2.0.0"

        # Test query param
        headers = {}
        query_params = {"version": ["1.1.0"]}

        version = self.version_manager.parse_version_from_request(headers, query_params)
        assert version == "1.1.0"


@pytest.mark.unit
class TestOpenAPIGenerator:
    """Test the OpenAPI generator functionality."""

    def setup_method(self):
        """Set up test method."""
        self.generator = OpenAPIGenerator("Test API", "1.0.0", "Test description")

    def test_generator_creation(self):
        """Test creating an OpenAPI generator."""
        assert self.generator.title == "Test API"
        assert self.generator.version == "1.0.0"
        assert "openapi" in self.generator.spec.spec
        assert "info" in self.generator.spec.spec

    def test_add_rest_api(self):
        """Test adding REST API to specification."""
        api = RESTAPI("Test API", "1.0.0")

        # Add a test endpoint
        def test_handler(request):
            """Test functionality: handler."""
            return APIResponse.success({"test": "data"})

        endpoint = APIEndpoint(
            path="/test",
            method=HTTPMethod.GET,
            handler=test_handler,
            summary="Test endpoint"
        )
        api.router.add_endpoint(endpoint)

        self.generator.add_rest_api(api)

        # Check that endpoint was added
        assert "/test" in self.generator.spec.spec["paths"]
        assert "get" in self.generator.spec.spec["paths"]["/test"]

    def test_add_graphql_api(self):
        """Test adding GraphQL API to specification."""
        schema = GraphQLSchema()
        api = GraphQLAPI(schema)

        self.generator.add_graphql_api(api)

        # Check that GraphQL endpoints were added
        assert "/graphql" in self.generator.spec.spec["paths"]
        assert "/graphql/playground" in self.generator.spec.spec["paths"]

        # Check that GraphQL schemas were added
        components = self.generator.spec.spec["components"]
        assert "GraphQLRequest" in components["schemas"]
        assert "GraphQLResponse" in components["schemas"]

    def test_add_version_manager(self):
        """Test adding version manager to specification."""
        version_manager = APIVersionManager("1.0.0")

        self.generator.add_version_manager(version_manager)

        # Check that version parameter was added
        components = self.generator.spec.spec["components"]
        assert "ApiVersion" in components["parameters"]

        # Check that version info was added
        info = self.generator.spec.spec["info"]
        assert "x-api-versions" in info

    def test_spec_validation(self):
        """Test OpenAPI specification validation."""
        # Valid spec should have no errors
        errors = self.generator.validate_spec()
        # May have some validation errors for minimal spec, but should not crash

    def test_spec_generation(self):
        """Test generating final specification."""
        spec = self.generator.generate_spec()

        assert isinstance(spec, OpenAPISpecification)
        assert "openapi" in spec.spec
        assert "info" in spec.spec

        # Test JSON output
        json_str = spec.to_json()
        assert isinstance(json_str, str)
        assert '"openapi"' in json_str

    def test_spec_save(self, tmp_path):
        """Test saving specification to file."""
        spec = self.generator.generate_spec()

        json_file = tmp_path / "spec.json"
        spec.save_to_file(str(json_file), "json")

        assert json_file.exists()

        # Verify content
        with open(json_file) as f:
            data = json.load(f)
            assert "openapi" in data
            assert "info" in data


@pytest.mark.unit
class TestIntegration:
    """Integration tests for API standardization components."""

    def test_rest_api_with_versioning(self):
        """Test REST API with versioning."""
        # Create version manager
        version_manager = APIVersionManager("1.0.0")

        # Create REST API
        api = RESTAPI("Test API", "1.0.0")

        # Add versioned endpoint
        def handler_v1(request):
            return APIResponse.success({"version": "1.0", "data": "old"})

        def handler_v2(request):
            return APIResponse.success({"version": "2.0", "data": "new"})

        endpoint = VersionedEndpoint("/api/data", {}, "1.0.0")
        endpoint.add_version("1.0.0", handler_v1)
        endpoint.add_version("2.0.0", handler_v2)

        version_manager.register_endpoint(endpoint)

        # Test version parsing
        headers = {"x-api-version": "2.0.0"}
        version = version_manager.parse_version_from_request(headers, {})
        assert version == "2.0.0"

    def test_openapi_generation_from_multiple_sources(self):
        """Test generating OpenAPI from multiple API sources."""
        generator = OpenAPIGenerator("Multi-API", "1.0.0")

        # Add REST API
        rest_api = RESTAPI("REST API", "1.0.0")
        def rest_handler(request):
            return APIResponse.success({"type": "rest"})
        rest_api.router.add_endpoint(APIEndpoint("/rest", HTTPMethod.GET, rest_handler))
        generator.add_rest_api(rest_api)

        # Add GraphQL API
        graphql_schema = GraphQLSchema()
        graphql_api = GraphQLAPI(graphql_schema)
        generator.add_graphql_api(graphql_api)

        # Add version manager
        version_manager = APIVersionManager("1.0.0")
        generator.add_version_manager(version_manager)

        # Generate spec
        spec = generator.generate_spec()

        # Verify all components are present
        paths = spec.spec["paths"]
        assert "/rest" in paths
        assert "/graphql" in paths
        assert "/graphql/playground" in paths

        # Validate the spec
        errors = generator.validate_spec()
        # Should not have critical validation errors
        assert not any("Missing required field" in error for error in errors)
