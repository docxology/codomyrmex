"""Tests for DocumentationOpenAPIGenerator."""

import json
import os
import tempfile

import pytest

from codomyrmex.api.openapi_generator import (
    DocumentationOpenAPIGenerator,
)

# ---------------------------------------------------------------------------
# DocumentationOpenAPIGenerator
# ---------------------------------------------------------------------------

class TestDocGenMultipleEndpoints:
    """Tests for multiple-endpoint and complex endpoint scenarios."""

    @pytest.mark.unit
    def test_multiple_methods_same_path(self):
        """GET and POST on the same path both appear in spec."""
        gen = DocumentationOpenAPIGenerator()
        endpoints = [
            {"path": "/items", "method": "GET", "summary": "List items"},
            {"path": "/items", "method": "POST", "summary": "Create item"},
        ]
        spec = gen.generate_spec("API", "1.0.0", endpoints)
        assert "get" in spec["paths"]["/items"]
        assert "post" in spec["paths"]["/items"]

    @pytest.mark.unit
    def test_endpoint_with_request_body(self):
        """Endpoint containing requestBody should propagate."""
        gen = DocumentationOpenAPIGenerator()
        body = {"required": True, "content": {"application/json": {"schema": {"type": "object"}}}}
        endpoints = [
            {
                "path": "/users",
                "method": "POST",
                "requestBody": body,
                "responses": {"201": {"description": "Created"}},
            },
        ]
        spec = gen.generate_spec("API", "1.0.0", endpoints)
        assert spec["paths"]["/users"]["post"]["requestBody"] == body

    @pytest.mark.unit
    def test_endpoint_without_request_body(self):
        """Endpoint without requestBody should NOT have the key."""
        gen = DocumentationOpenAPIGenerator()
        endpoints = [{"path": "/ping", "method": "GET"}]
        spec = gen.generate_spec("API", "1.0.0", endpoints)
        assert "requestBody" not in spec["paths"]["/ping"]["get"]

    @pytest.mark.unit
    def test_endpoint_with_security(self):
        """Endpoint with security field should propagate."""
        gen = DocumentationOpenAPIGenerator()
        sec = [{"BearerAuth": []}]
        endpoints = [
            {
                "path": "/secure",
                "method": "GET",
                "security": sec,
                "responses": {"200": {"description": "OK"}},
            },
        ]
        spec = gen.generate_spec("API", "1.0.0", endpoints)
        assert spec["paths"]["/secure"]["get"]["security"] == sec

    @pytest.mark.unit
    def test_endpoint_without_security(self):
        """Endpoint without security should NOT add the key."""
        gen = DocumentationOpenAPIGenerator()
        endpoints = [{"path": "/open", "method": "GET"}]
        spec = gen.generate_spec("API", "1.0.0", endpoints)
        assert "security" not in spec["paths"]["/open"]["get"]

    @pytest.mark.unit
    def test_endpoint_default_response(self):
        """Endpoint missing responses should get default 200/Success."""
        gen = DocumentationOpenAPIGenerator()
        endpoints = [{"path": "/def", "method": "GET"}]
        spec = gen.generate_spec("API", "1.0.0", endpoints)
        assert spec["paths"]["/def"]["get"]["responses"] == {"200": {"description": "Success"}}

    @pytest.mark.unit
    def test_endpoint_custom_responses(self):
        """Endpoint with explicit responses should use those."""
        gen = DocumentationOpenAPIGenerator()
        custom = {"201": {"description": "Created"}, "400": {"description": "Bad"}}
        endpoints = [{"path": "/custom", "method": "POST", "responses": custom}]
        spec = gen.generate_spec("API", "1.0.0", endpoints)
        assert spec["paths"]["/custom"]["post"]["responses"] == custom

    @pytest.mark.unit
    def test_endpoint_with_parameters(self):
        """Parameters list should pass through."""
        gen = DocumentationOpenAPIGenerator()
        params = [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}]
        endpoints = [{"path": "/users/{id}", "method": "GET", "parameters": params}]
        spec = gen.generate_spec("API", "1.0.0", endpoints)
        assert spec["paths"]["/users/{id}"]["get"]["parameters"] == params

    @pytest.mark.unit
    def test_endpoint_object_with_to_dict(self):
        """If an endpoint has a to_dict method, the generator calls it."""

        class FakeEndpoint:
            def to_dict(self):
                return {"path": "/fake", "method": "DELETE", "summary": "Fake delete"}

        gen = DocumentationOpenAPIGenerator()
        spec = gen.generate_spec("API", "1.0.0", [FakeEndpoint()])
        assert "delete" in spec["paths"]["/fake"]
        assert spec["paths"]["/fake"]["delete"]["summary"] == "Fake delete"

    @pytest.mark.unit
    def test_spec_info_auto_description(self):
        """Info description should be auto-generated from title."""
        gen = DocumentationOpenAPIGenerator()
        spec = gen.generate_spec("My Awesome API", "1.0.0", [])
        assert "My Awesome API" in spec["info"]["description"]

    @pytest.mark.unit
    def test_spec_servers_from_base_url(self):
        """Servers list should contain the provided base_url."""
        gen = DocumentationOpenAPIGenerator()
        spec = gen.generate_spec("API", "1.0.0", [], base_url="https://api.example.com")
        assert spec["servers"][0]["url"] == "https://api.example.com"

    @pytest.mark.unit
    def test_spec_contains_default_schemas(self):
        """Generated spec should include Error and Success schemas."""
        gen = DocumentationOpenAPIGenerator()
        spec = gen.generate_spec("API", "1.0.0", [])
        schemas = spec["components"]["schemas"]
        assert "Error" in schemas
        assert "Success" in schemas

    @pytest.mark.unit
    def test_spec_contains_default_security_schemes(self):
        """Generated spec should include BearerAuth, ApiKeyAuth, BasicAuth."""
        gen = DocumentationOpenAPIGenerator()
        spec = gen.generate_spec("API", "1.0.0", [])
        ss = spec["components"]["securitySchemes"]
        assert "BearerAuth" in ss
        assert "ApiKeyAuth" in ss
        assert "BasicAuth" in ss

    @pytest.mark.unit
    def test_default_schemas_error_required_fields(self):
        """Error schema must require 'error' and 'message'."""
        gen = DocumentationOpenAPIGenerator()
        schemas = gen._get_default_schemas()
        assert schemas["Error"]["required"] == ["error", "message"]

    @pytest.mark.unit
    def test_default_schemas_success_required_fields(self):
        """Success schema must require 'success'."""
        gen = DocumentationOpenAPIGenerator()
        schemas = gen._get_default_schemas()
        assert schemas["Success"]["required"] == ["success"]

    @pytest.mark.unit
    def test_default_security_bearer_format(self):
        """BearerAuth scheme must have JWT format."""
        gen = DocumentationOpenAPIGenerator()
        ss = gen._get_default_security_schemes()
        assert ss["BearerAuth"]["bearerFormat"] == "JWT"

    @pytest.mark.unit
    def test_default_security_apikey_location(self):
        """ApiKeyAuth must be in header with name X-API-Key."""
        gen = DocumentationOpenAPIGenerator()
        ss = gen._get_default_security_schemes()
        assert ss["ApiKeyAuth"]["in"] == "header"
        assert ss["ApiKeyAuth"]["name"] == "X-API-Key"


# ---------------------------------------------------------------------------
# DocumentationOpenAPIGenerator -- validate_spec
# ---------------------------------------------------------------------------

class TestDocGenValidateSpec:
    """Thorough validation tests for DocumentationOpenAPIGenerator.validate_spec."""

    @pytest.mark.unit
    def test_valid_spec_returns_no_errors(self):
        """A fully valid spec should produce an empty error list."""
        gen = DocumentationOpenAPIGenerator()
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "T", "version": "1.0.0"},
            "paths": {
                "/a": {"get": {"responses": {"200": {"description": "OK"}}}}
            },
        }
        assert gen.validate_spec(spec) == []

    @pytest.mark.unit
    def test_missing_openapi_field(self):
        """Missing 'openapi' key should produce an error."""
        gen = DocumentationOpenAPIGenerator()
        spec = {"info": {"title": "T", "version": "1"}, "paths": {}}
        errors = gen.validate_spec(spec)
        assert any("openapi" in e for e in errors)

    @pytest.mark.unit
    def test_missing_info_field(self):
        """Missing 'info' key should produce an error."""
        gen = DocumentationOpenAPIGenerator()
        spec = {"openapi": "3.0.3", "paths": {}}
        errors = gen.validate_spec(spec)
        assert any("info" in e for e in errors)

    @pytest.mark.unit
    def test_missing_paths_field(self):
        """Missing 'paths' key should produce an error."""
        gen = DocumentationOpenAPIGenerator()
        spec = {"openapi": "3.0.3", "info": {"title": "T", "version": "1"}}
        errors = gen.validate_spec(spec)
        assert any("paths" in e for e in errors)

    @pytest.mark.unit
    def test_info_not_dict(self):
        """Non-dict info should produce an error."""
        gen = DocumentationOpenAPIGenerator()
        spec = {"openapi": "3.0.3", "info": "not a dict", "paths": {}}
        errors = gen.validate_spec(spec)
        assert any("info must be an object" in e for e in errors)

    @pytest.mark.unit
    def test_info_missing_title(self):
        """Info dict missing title should produce an error."""
        gen = DocumentationOpenAPIGenerator()
        spec = {"openapi": "3.0.3", "info": {"version": "1"}, "paths": {}}
        errors = gen.validate_spec(spec)
        assert any("info.title" in e for e in errors)

    @pytest.mark.unit
    def test_info_missing_version(self):
        """Info dict missing version should produce an error."""
        gen = DocumentationOpenAPIGenerator()
        spec = {"openapi": "3.0.3", "info": {"title": "T"}, "paths": {}}
        errors = gen.validate_spec(spec)
        assert any("info.version" in e for e in errors)

    @pytest.mark.unit
    def test_invalid_http_method(self):
        """An invalid HTTP method should be flagged."""
        gen = DocumentationOpenAPIGenerator()
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "T", "version": "1"},
            "paths": {
                "/x": {"CONNECT": {"responses": {"200": {"description": "OK"}}}}
            },
        }
        errors = gen.validate_spec(spec)
        assert any("Invalid HTTP method" in e for e in errors)

    @pytest.mark.unit
    def test_path_not_starting_with_slash(self):
        """A path not starting with '/' should produce an error."""
        gen = DocumentationOpenAPIGenerator()
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "T", "version": "1"},
            "paths": {
                "no-slash": {"get": {"responses": {"200": {"description": "OK"}}}}
            },
        }
        errors = gen.validate_spec(spec)
        assert any("/" in e for e in errors)

    @pytest.mark.unit
    def test_non_dict_path_methods(self):
        """Path with non-dict methods value should produce error."""
        gen = DocumentationOpenAPIGenerator()
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "T", "version": "1"},
            "paths": {"/broken": "not a dict"},
        }
        errors = gen.validate_spec(spec)
        assert any("must be an object" in e for e in errors)

    @pytest.mark.unit
    def test_non_dict_operation(self):
        """Operation that is not a dict should produce error."""
        gen = DocumentationOpenAPIGenerator()
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "T", "version": "1"},
            "paths": {"/x": {"get": "not a dict"}},
        }
        errors = gen.validate_spec(spec)
        assert any("must be an object" in e for e in errors)

    @pytest.mark.unit
    def test_missing_responses_in_operation(self):
        """Operation with no responses key should produce error."""
        gen = DocumentationOpenAPIGenerator()
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "T", "version": "1"},
            "paths": {"/x": {"get": {"summary": "no responses"}}},
        }
        errors = gen.validate_spec(spec)
        assert any("responses" in e.lower() for e in errors)

    @pytest.mark.unit
    @pytest.mark.parametrize("method", ["get", "post", "put", "delete", "patch", "options", "head"])
    def test_all_valid_methods_accepted(self, method):
        """Each valid HTTP method should not produce a method error."""
        gen = DocumentationOpenAPIGenerator()
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "T", "version": "1"},
            "paths": {"/ok": {method: {"responses": {"200": {"description": "OK"}}}}},
        }
        errors = gen.validate_spec(spec)
        assert not any("Invalid HTTP method" in e for e in errors)

    @pytest.mark.unit
    def test_empty_spec_has_multiple_errors(self):
        """An empty dict should produce errors for openapi, info, and paths."""
        gen = DocumentationOpenAPIGenerator()
        errors = gen.validate_spec({})
        assert len(errors) >= 3


# ---------------------------------------------------------------------------
# DocumentationOpenAPIGenerator -- export_spec
# ---------------------------------------------------------------------------

class TestDocGenExport:
    """Tests for export_spec and HTML doc generation edge cases."""

    @pytest.mark.unit
    def test_export_spec_yaml(self):
        """export_spec with yaml format should produce a readable file."""
        gen = DocumentationOpenAPIGenerator()
        spec = gen.generate_spec("Export YAML Test", "1.0.0", [])
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "spec.yaml")
            result = gen.export_spec(spec, filepath, format="yaml")
            assert result is True
            with open(filepath) as f:
                content = f.read()
            assert "Export YAML Test" in content

    @pytest.mark.unit
    def test_export_spec_unsupported_format(self):
        """export_spec with unsupported format returns False."""
        gen = DocumentationOpenAPIGenerator()
        spec = gen.generate_spec("API", "1.0.0", [])
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "spec.xml")
            result = gen.export_spec(spec, filepath, format="xml")
            assert result is False

    @pytest.mark.unit
    def test_export_spec_creates_directories(self):
        """export_spec should create intermediate directories."""
        gen = DocumentationOpenAPIGenerator()
        spec = gen.generate_spec("API", "1.0.0", [])
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "sub", "dir", "spec.json")
            result = gen.export_spec(spec, filepath, format="json")
            assert result is True
            assert os.path.exists(filepath)

    @pytest.mark.unit
    def test_export_spec_json_content_valid(self):
        """Exported JSON file should be parseable and match original spec."""
        gen = DocumentationOpenAPIGenerator()
        spec = gen.generate_spec("Round", "2.0.0", [])
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "spec.json")
            gen.export_spec(spec, filepath, format="json")
            with open(filepath) as f:
                loaded = json.load(f)
            assert loaded["info"]["title"] == "Round"
            assert loaded["info"]["version"] == "2.0.0"

    @pytest.mark.unit
    def test_html_docs_contain_all_methods(self):
        """HTML docs should render endpoints with different methods."""
        gen = DocumentationOpenAPIGenerator()
        spec = {
            "info": {"title": "Multi", "version": "1.0.0", "description": "desc"},
            "paths": {
                "/a": {"get": {"summary": "Get A", "parameters": [], "responses": {}}},
                "/b": {"post": {"summary": "Post B", "parameters": [], "responses": {}}},
                "/c": {"delete": {"summary": "Del C", "parameters": [], "responses": {}}},
            },
        }
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            filepath = f.name
        try:
            gen.generate_html_docs(spec, filepath)
            with open(filepath) as f:
                html = f.read()
            assert "GET" in html
            assert "POST" in html
            assert "DELETE" in html
            assert "/a" in html
            assert "/b" in html
            assert "/c" in html
        finally:
            os.unlink(filepath)

    @pytest.mark.unit
    def test_html_docs_contain_parameters(self):
        """HTML docs should render parameter names and descriptions."""
        gen = DocumentationOpenAPIGenerator()
        spec = {
            "info": {"title": "Params", "version": "1.0.0"},
            "paths": {
                "/search": {
                    "get": {
                        "summary": "Search",
                        "parameters": [
                            {"name": "query", "description": "Search term"},
                            {"name": "limit", "description": "Max results"},
                        ],
                        "responses": {},
                    }
                }
            },
        }
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            filepath = f.name
        try:
            gen.generate_html_docs(spec, filepath)
            with open(filepath) as f:
                html = f.read()
            assert "query" in html
            assert "limit" in html
            assert "Search term" in html
        finally:
            os.unlink(filepath)
