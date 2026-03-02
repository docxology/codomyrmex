"""Tests for StandardizationOpenAPIGenerator."""

import json
import os
import tempfile

import pytest

from codomyrmex.api.openapi_generator import (
    DocumentationOpenAPIGenerator,
    OpenAPISpecification,
    StandardizationOpenAPIGenerator,
    create_openapi_generator,
    generate_openapi_spec,
    validate_openapi_spec,
)

# ---------------------------------------------------------------------------
# StandardizationOpenAPIGenerator
# ---------------------------------------------------------------------------

class TestStdGenInitialization:
    """Initialization and basic attribute tests for StandardizationOpenAPIGenerator."""

    @pytest.mark.unit
    def test_default_initialization(self):
        """Default init should populate title, version, description, base_url."""
        gen = StandardizationOpenAPIGenerator()
        assert gen.title == "Codomyrmex API"
        assert gen.version == "1.0.0"
        assert gen.description == "API for Codomyrmex"
        assert gen.base_url == "/api"

    @pytest.mark.unit
    def test_custom_initialization(self):
        """Custom init should set all fields."""
        gen = StandardizationOpenAPIGenerator(
            title="Custom",
            version="3.0.0",
            description="Custom API",
            base_url="/v3/api/",
        )
        assert gen.title == "Custom"
        assert gen.version == "3.0.0"
        assert gen.description == "Custom API"
        # Trailing slash should be stripped
        assert gen.base_url == "/v3/api"

    @pytest.mark.unit
    def test_initial_spec_structure(self):
        """Freshly created generator should have openapi, info, paths, components, tags."""
        gen = StandardizationOpenAPIGenerator()
        s = gen.spec.spec
        assert s["openapi"] == "3.0.3"
        assert s["info"]["title"] == "Codomyrmex API"
        assert s["paths"] == {}
        assert "schemas" in s["components"]
        assert "responses" in s["components"]
        assert "parameters" in s["components"]
        assert s["tags"] == []


class TestStdGenAddMethods:
    """Tests for add_* methods on StandardizationOpenAPIGenerator."""

    @pytest.mark.unit
    def test_add_multiple_security_schemes(self):
        """Multiple add_security_schemes calls should merge."""
        gen = StandardizationOpenAPIGenerator()
        gen.add_security_schemes({"A": {"type": "http"}})
        gen.add_security_schemes({"B": {"type": "apiKey"}})
        ss = gen.spec.spec["components"]["securitySchemes"]
        assert "A" in ss
        assert "B" in ss

    @pytest.mark.unit
    def test_add_security_schemes_creates_key(self):
        """If securitySchemes key doesn't exist, add_security_schemes should create it."""
        gen = StandardizationOpenAPIGenerator()
        # Remove the key to test creation branch
        gen.spec.spec["components"].pop("securitySchemes", None)
        gen.add_security_schemes({"OAuth": {"type": "oauth2"}})
        assert "OAuth" in gen.spec.spec["components"]["securitySchemes"]

    @pytest.mark.unit
    def test_add_tags_appends(self):
        """Multiple add_tags calls should accumulate."""
        gen = StandardizationOpenAPIGenerator()
        gen.add_tags([{"name": "users"}])
        gen.add_tags([{"name": "items"}])
        names = [t["name"] for t in gen.spec.spec["tags"]]
        assert "users" in names
        assert "items" in names

    @pytest.mark.unit
    def test_add_global_responses_merges(self):
        """Multiple add_global_responses calls should merge."""
        gen = StandardizationOpenAPIGenerator()
        gen.add_global_responses({"NotFound": {"description": "404"}})
        gen.add_global_responses({"ServerError": {"description": "500"}})
        r = gen.spec.spec["components"]["responses"]
        assert "NotFound" in r
        assert "ServerError" in r

    @pytest.mark.unit
    def test_set_external_docs_fields(self):
        """set_external_docs should populate url and description."""
        gen = StandardizationOpenAPIGenerator()
        gen.set_external_docs("https://example.com/docs", "Full docs")
        ed = gen.spec.spec["externalDocs"]
        assert ed["url"] == "https://example.com/docs"
        assert ed["description"] == "Full docs"

    @pytest.mark.unit
    def test_set_external_docs_default_description(self):
        """set_external_docs with no description arg should use default text."""
        gen = StandardizationOpenAPIGenerator()
        gen.set_external_docs("https://example.com")
        ed = gen.spec.spec["externalDocs"]
        assert "Find out more" in ed["description"]


class TestStdGenValidateSpec:
    """Validation tests for StandardizationOpenAPIGenerator.validate_spec."""

    @pytest.mark.unit
    def test_fresh_generator_valid(self):
        """A freshly created generator should have zero validation errors."""
        gen = StandardizationOpenAPIGenerator()
        errors = gen.validate_spec()
        assert errors == []

    @pytest.mark.unit
    def test_missing_required_field_detected(self):
        """Removing 'openapi' should cause a validation error."""
        gen = StandardizationOpenAPIGenerator()
        del gen.spec.spec["openapi"]
        errors = gen.validate_spec()
        assert any("openapi" in e for e in errors)

    @pytest.mark.unit
    def test_invalid_method_detected(self):
        """Adding an invalid HTTP method should be flagged."""
        gen = StandardizationOpenAPIGenerator()
        gen.spec.spec["paths"]["/x"] = {
            "CONNECT": {"responses": {"200": {"description": "OK"}}}
        }
        errors = gen.validate_spec()
        assert any("Invalid HTTP method" in e for e in errors)

    @pytest.mark.unit
    def test_missing_responses_detected(self):
        """Operation without responses should be flagged."""
        gen = StandardizationOpenAPIGenerator()
        gen.spec.spec["paths"]["/y"] = {"get": {"summary": "no responses"}}
        errors = gen.validate_spec()
        assert any("Missing responses" in e for e in errors)

    @pytest.mark.unit
    def test_invalid_path_definition(self):
        """Non-dict path value should be flagged."""
        gen = StandardizationOpenAPIGenerator()
        gen.spec.spec["paths"]["/bad"] = "string, not dict"
        errors = gen.validate_spec()
        assert any("Invalid path definition" in e for e in errors)


class TestStdGenGenerateSpec:
    """Tests for StandardizationOpenAPIGenerator.generate_spec."""

    @pytest.mark.unit
    def test_generate_spec_adds_metadata(self):
        """generate_spec should add x-generated-at and x-generator."""
        gen = StandardizationOpenAPIGenerator(title="Meta", version="1.0.0")
        spec = gen.generate_spec()
        assert "x-generated-at" in spec.spec["info"]
        assert spec.spec["info"]["x-generator"] == "Codomyrmex OpenAPI Generator"

    @pytest.mark.unit
    def test_generate_spec_returns_openapi_specification(self):
        """generate_spec should return an OpenAPISpecification instance."""
        gen = StandardizationOpenAPIGenerator()
        spec = gen.generate_spec()
        assert isinstance(spec, OpenAPISpecification)

    @pytest.mark.unit
    def test_generate_spec_preserves_paths(self):
        """Paths added before generate_spec should be present in output."""
        gen = StandardizationOpenAPIGenerator()
        gen.spec.spec["paths"]["/kept"] = {
            "get": {"responses": {"200": {"description": "OK"}}}
        }
        spec = gen.generate_spec()
        assert "/kept" in spec.spec["paths"]


# ---------------------------------------------------------------------------
# StandardizationOpenAPIGenerator with real REST API
# ---------------------------------------------------------------------------

class TestStdGenRESTIntegration:
    """Tests for add_rest_api with real RESTAPI objects."""

    @pytest.mark.unit
    def test_add_rest_api_populates_paths(self):
        """Adding a REST API with endpoints should populate spec paths."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI,
            APIEndpoint,
            APIResponse,
            HTTPMethod,
        )

        api = RESTAPI(title="Test", version="1.0.0")

        def handler(req):
            return APIResponse.success({})

        ep = APIEndpoint(
            path="/widgets",
            method=HTTPMethod.GET,
            handler=handler,
            summary="List widgets",
            description="Get all widgets",
        )
        api.router.add_endpoint(ep)

        gen = StandardizationOpenAPIGenerator()
        gen.add_rest_api(api)

        assert "/widgets" in gen.spec.spec["paths"]
        assert "get" in gen.spec.spec["paths"]["/widgets"]

    @pytest.mark.unit
    def test_add_rest_api_sets_servers(self):
        """add_rest_api should set the servers list."""
        from codomyrmex.api.standardization.rest_api import RESTAPI

        api = RESTAPI(title="SrvTest", version="2.0.0")
        gen = StandardizationOpenAPIGenerator(base_url="/v2")
        gen.add_rest_api(api)

        assert gen.spec.spec["servers"][0]["url"] == "/v2"

    @pytest.mark.unit
    def test_add_rest_api_rejects_object_without_get_endpoints(self):
        """Object missing get_endpoints method should raise TypeError."""
        gen = StandardizationOpenAPIGenerator()

        class BadAPI:
            pass

        with pytest.raises(TypeError, match="get_endpoints"):
            gen.add_rest_api(BadAPI())

    @pytest.mark.unit
    def test_rest_endpoint_with_tags(self):
        """Endpoint tags should appear in the generated spec."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI,
            APIEndpoint,
            APIResponse,
            HTTPMethod,
        )

        api = RESTAPI(title="Tagged", version="1.0.0")

        def handler(req):
            return APIResponse.success({})

        ep = APIEndpoint(
            path="/tagged",
            method=HTTPMethod.POST,
            handler=handler,
            tags=["admin", "internal"],
        )
        api.router.add_endpoint(ep)

        gen = StandardizationOpenAPIGenerator()
        gen.add_rest_api(api)
        assert gen.spec.spec["paths"]["/tagged"]["post"]["tags"] == ["admin", "internal"]

    @pytest.mark.unit
    def test_rest_endpoint_with_parameters(self):
        """Endpoint parameters should appear in the generated spec."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI,
            APIEndpoint,
            APIResponse,
            HTTPMethod,
        )

        api = RESTAPI(title="Params", version="1.0.0")

        def handler(req):
            return APIResponse.success({})

        params = [{"name": "page", "in": "query", "schema": {"type": "integer"}}]
        ep = APIEndpoint(
            path="/list",
            method=HTTPMethod.GET,
            handler=handler,
            parameters=params,
        )
        api.router.add_endpoint(ep)

        gen = StandardizationOpenAPIGenerator()
        gen.add_rest_api(api)
        assert gen.spec.spec["paths"]["/list"]["get"]["parameters"] == params

    @pytest.mark.unit
    def test_rest_endpoint_default_responses(self):
        """Endpoint with no responses gets 200, 400, 500 defaults."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI,
            APIEndpoint,
            APIResponse,
            HTTPMethod,
        )

        api = RESTAPI(title="DefResp", version="1.0.0")

        def handler(req):
            return APIResponse.success({})

        ep = APIEndpoint(
            path="/default",
            method=HTTPMethod.GET,
            handler=handler,
        )
        api.router.add_endpoint(ep)

        gen = StandardizationOpenAPIGenerator()
        gen.add_rest_api(api)
        responses = gen.spec.spec["paths"]["/default"]["get"]["responses"]
        assert "200" in responses
        assert "400" in responses
        assert "500" in responses

    @pytest.mark.unit
    def test_rest_endpoint_summary_fallback(self):
        """Endpoint with no summary should get method+path as fallback."""
        from codomyrmex.api.standardization.rest_api import (
            RESTAPI,
            APIEndpoint,
            APIResponse,
            HTTPMethod,
        )

        api = RESTAPI(title="Fallback", version="1.0.0")

        def handler(req):
            return APIResponse.success({})

        ep = APIEndpoint(
            path="/nosummary",
            method=HTTPMethod.PUT,
            handler=handler,
        )
        api.router.add_endpoint(ep)

        gen = StandardizationOpenAPIGenerator()
        gen.add_rest_api(api)
        summary = gen.spec.spec["paths"]["/nosummary"]["put"]["summary"]
        assert "PUT" in summary
        assert "/nosummary" in summary


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @pytest.mark.unit
    def test_create_openapi_generator_defaults(self):
        """create_openapi_generator() should return a generator with default params."""
        gen = create_openapi_generator()
        assert isinstance(gen, StandardizationOpenAPIGenerator)
        assert gen.title == "Codomyrmex API"
        assert gen.version == "1.0.0"

    @pytest.mark.unit
    def test_create_openapi_generator_custom(self):
        """create_openapi_generator with custom args should propagate."""
        gen = create_openapi_generator(title="Custom", version="2.0.0", description="Desc")
        assert gen.title == "Custom"
        assert gen.version == "2.0.0"

    @pytest.mark.unit
    def test_generate_openapi_spec_returns_dict(self):
        """generate_openapi_spec should return a dict with openapi key."""
        spec = generate_openapi_spec("Quick", "1.0.0", [])
        assert isinstance(spec, dict)
        assert spec["openapi"] == "3.0.3"

    @pytest.mark.unit
    def test_generate_openapi_spec_with_endpoints(self):
        """generate_openapi_spec with endpoints should populate paths."""
        endpoints = [
            {"path": "/health", "method": "GET", "summary": "Health check"},
        ]
        spec = generate_openapi_spec("Health API", "1.0.0", endpoints)
        assert "/health" in spec["paths"]

    @pytest.mark.unit
    def test_validate_openapi_spec_valid(self):
        """validate_openapi_spec on a valid spec should return empty list."""
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "T", "version": "1"},
            "paths": {"/x": {"get": {"responses": {"200": {"description": "OK"}}}}},
        }
        assert validate_openapi_spec(spec) == []

    @pytest.mark.unit
    def test_validate_openapi_spec_invalid(self):
        """validate_openapi_spec on broken spec should return errors."""
        errors = validate_openapi_spec({})
        assert len(errors) >= 3


# ---------------------------------------------------------------------------
# GraphQL integration with StandardizationOpenAPIGenerator
# ---------------------------------------------------------------------------

class TestStdGenGraphQLIntegration:
    """Tests for add_graphql_api with real GraphQL objects."""

    @pytest.mark.unit
    def test_add_graphql_api_adds_paths(self):
        """add_graphql_api should create /graphql and /graphql/playground paths."""
        from codomyrmex.api.standardization.graphql_api import GraphQLAPI, GraphQLSchema

        schema = GraphQLSchema()
        api = GraphQLAPI(schema)

        gen = StandardizationOpenAPIGenerator()
        gen.add_graphql_api(api)

        assert "/graphql" in gen.spec.spec["paths"]
        assert "/graphql/playground" in gen.spec.spec["paths"]

    @pytest.mark.unit
    def test_add_graphql_api_adds_request_response_schemas(self):
        """add_graphql_api should add GraphQLRequest and GraphQLResponse schemas."""
        from codomyrmex.api.standardization.graphql_api import GraphQLAPI, GraphQLSchema

        schema = GraphQLSchema()
        api = GraphQLAPI(schema)

        gen = StandardizationOpenAPIGenerator()
        gen.add_graphql_api(api)

        schemas = gen.spec.spec["components"]["schemas"]
        assert "GraphQLRequest" in schemas
        assert "GraphQLResponse" in schemas
        assert "GraphQLError" in schemas
        assert "GraphQLLocation" in schemas

    @pytest.mark.unit
    def test_graphql_request_schema_structure(self):
        """GraphQLRequest schema should require 'query' field."""
        from codomyrmex.api.standardization.graphql_api import GraphQLAPI, GraphQLSchema

        schema = GraphQLSchema()
        api = GraphQLAPI(schema)

        gen = StandardizationOpenAPIGenerator()
        gen.add_graphql_api(api)

        req_schema = gen.spec.spec["components"]["schemas"]["GraphQLRequest"]
        assert req_schema["required"] == ["query"]
        assert "query" in req_schema["properties"]
        assert "variables" in req_schema["properties"]
        assert "operationName" in req_schema["properties"]

    @pytest.mark.unit
    def test_graphql_with_custom_types(self):
        """GraphQL custom types should be converted to OpenAPI schemas."""
        from codomyrmex.api.standardization.graphql_api import (
            GraphQLAPI,
            GraphQLField,
            GraphQLObjectType,
            GraphQLSchema,
        )

        user_type = GraphQLObjectType(name="User", description="A user")
        user_type.add_field(GraphQLField(name="id", type="ID", description="User ID"))
        user_type.add_field(GraphQLField(name="name", type="String", description="User name"))

        schema = GraphQLSchema()
        schema.add_type(user_type)
        api = GraphQLAPI(schema)

        gen = StandardizationOpenAPIGenerator()
        gen.add_graphql_api(api)

        schemas = gen.spec.spec["components"]["schemas"]
        assert "User" in schemas
        assert "id" in schemas["User"]["properties"]
        assert "name" in schemas["User"]["properties"]
        assert schemas["User"]["description"] == "A user"

    @pytest.mark.unit
    def test_graphql_type_field_mapping(self):
        """GraphQL built-in types should map to correct OpenAPI types."""
        from codomyrmex.api.standardization.graphql_api import (
            GraphQLAPI,
            GraphQLField,
            GraphQLObjectType,
            GraphQLSchema,
        )

        type_def = GraphQLObjectType(name="TypeTest")
        type_def.add_field(GraphQLField(name="s", type="String"))
        type_def.add_field(GraphQLField(name="i", type="Int"))
        type_def.add_field(GraphQLField(name="f", type="Float"))
        type_def.add_field(GraphQLField(name="b", type="Boolean"))
        type_def.add_field(GraphQLField(name="id", type="ID"))

        schema = GraphQLSchema()
        schema.add_type(type_def)
        api = GraphQLAPI(schema)

        gen = StandardizationOpenAPIGenerator()
        gen.add_graphql_api(api)

        props = gen.spec.spec["components"]["schemas"]["TypeTest"]["properties"]
        assert props["s"]["type"] == "string"
        assert props["i"]["type"] == "integer"
        assert props["f"]["type"] == "number"
        assert props["b"]["type"] == "boolean"
        assert props["id"]["type"] == "string"

    @pytest.mark.unit
    def test_graphql_field_description_propagates(self):
        """GraphQL field descriptions should appear in OpenAPI schema."""
        from codomyrmex.api.standardization.graphql_api import (
            GraphQLAPI,
            GraphQLField,
            GraphQLObjectType,
            GraphQLSchema,
        )

        t = GraphQLObjectType(name="Described")
        t.add_field(GraphQLField(name="x", type="String", description="X field"))

        schema = GraphQLSchema()
        schema.add_type(t)
        api = GraphQLAPI(schema)

        gen = StandardizationOpenAPIGenerator()
        gen.add_graphql_api(api)

        assert gen.spec.spec["components"]["schemas"]["Described"]["properties"]["x"]["description"] == "X field"


# ---------------------------------------------------------------------------
# End-to-end workflow tests
# ---------------------------------------------------------------------------

class TestEndToEndWorkflow:
    """Full workflow tests combining multiple features."""

    @pytest.mark.unit
    def test_full_documentation_workflow(self):
        """Generate, validate, export, and verify a complete spec."""
        gen = DocumentationOpenAPIGenerator()
        endpoints = [
            {
                "path": "/users",
                "method": "GET",
                "summary": "List users",
                "parameters": [{"name": "limit", "in": "query"}],
                "responses": {"200": {"description": "OK"}},
            },
            {
                "path": "/users",
                "method": "POST",
                "summary": "Create user",
                "requestBody": {"content": {"application/json": {"schema": {"type": "object"}}}},
                "responses": {"201": {"description": "Created"}},
            },
            {
                "path": "/users/{id}",
                "method": "GET",
                "summary": "Get user",
                "parameters": [{"name": "id", "in": "path", "required": True}],
                "responses": {"200": {"description": "OK"}, "404": {"description": "Not found"}},
            },
            {
                "path": "/users/{id}",
                "method": "DELETE",
                "summary": "Delete user",
                "security": [{"BearerAuth": []}],
                "responses": {"204": {"description": "Deleted"}},
            },
        ]

        spec = gen.generate_spec("User API", "1.0.0", endpoints, base_url="https://api.example.com")

        # Validate
        errors = gen.validate_spec(spec)
        assert errors == []

        # Verify structure
        assert spec["openapi"] == "3.0.3"
        assert len(spec["paths"]) == 2  # /users and /users/{id}
        assert len(spec["paths"]["/users"]) == 2  # GET and POST
        assert len(spec["paths"]["/users/{id}"]) == 2  # GET and DELETE

        # Export and verify
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "user_api.json")
            result = gen.export_spec(spec, filepath, format="json")
            assert result is True
            with open(filepath) as f:
                loaded = json.load(f)
            assert loaded["info"]["title"] == "User API"

    @pytest.mark.unit
    def test_full_standardization_workflow(self):
        """Build a complete spec using StandardizationOpenAPIGenerator."""
        gen = StandardizationOpenAPIGenerator(
            title="Widget API",
            version="2.0.0",
            description="Widget management service",
            base_url="/api/v2",
        )

        gen.add_security_schemes({
            "BearerAuth": {"type": "http", "scheme": "bearer"},
        })

        gen.add_tags([
            {"name": "widgets", "description": "Widget CRUD"},
            {"name": "admin", "description": "Administration"},
        ])

        gen.add_global_responses({
            "Unauthorized": {"description": "Authentication required"},
        })

        gen.set_external_docs("https://docs.widgets.io")

        # Validate before generation
        errors = gen.validate_spec()
        assert errors == []

        # Generate
        spec = gen.generate_spec()
        assert isinstance(spec, OpenAPISpecification)
        assert spec.spec["info"]["title"] == "Widget API"
        assert "x-generated-at" in spec.spec["info"]
        assert len(spec.spec["tags"]) == 2
        assert "BearerAuth" in spec.spec["components"]["securitySchemes"]
        assert "Unauthorized" in spec.spec["components"]["responses"]
        assert spec.spec["externalDocs"]["url"] == "https://docs.widgets.io"
