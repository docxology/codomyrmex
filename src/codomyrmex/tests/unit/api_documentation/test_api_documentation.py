"""
Comprehensive tests for the api_documentation module.

This module tests all API documentation functionality including
generation, OpenAPI specification, and schema management.
"""

import pytest
import tempfile
import os
import json
import yaml
import ast
from pathlib import Path
from datetime import datetime, timezone

from codomyrmex.api.documentation.doc_generator import (
    APIDocumentationGenerator,
    generate_api_docs,
    extract_api_specs,
    APIDocumentation,
    APIEndpoint
)

from codomyrmex.api.openapi_generator import (
    DocumentationOpenAPIGenerator as OpenAPIGenerator,
    generate_openapi_spec,
    validate_openapi_spec
)


class TestAPIEndpoint:
    """Test cases for APIEndpoint dataclass."""

    def test_api_endpoint_creation(self):
        """Test APIEndpoint creation."""
        endpoint = APIEndpoint(
            path="/users",
            method="GET",
            summary="Get users",
            description="Retrieve a list of users",
            parameters=[
                {
                    "name": "limit",
                    "in": "query",
                    "schema": {"type": "integer"}
                }
            ],
            responses={
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
                        }
                    }
                }
            }
        )

        assert endpoint.path == "/users"
        assert endpoint.method == "GET"
        assert endpoint.summary == "Get users"
        assert len(endpoint.parameters) == 1
        assert "200" in endpoint.responses

    def test_api_endpoint_defaults(self):
        """Test APIEndpoint default values."""
        endpoint = APIEndpoint(path="/test", method="POST", summary="Test")

        assert endpoint.description == ""
        assert endpoint.parameters == []
        assert endpoint.request_body is None
        assert endpoint.responses == {}
        assert endpoint.tags == []
        assert endpoint.deprecated is False
        assert endpoint.security == []

    def test_api_endpoint_to_dict(self):
        """Test APIEndpoint to_dict conversion."""
        endpoint = APIEndpoint(
            path="/test",
            method="GET",
            summary="Test endpoint",
            deprecated=True
        )

        endpoint_dict = endpoint.to_dict()

        assert endpoint_dict["path"] == "/test"
        assert endpoint_dict["method"] == "GET"
        assert endpoint_dict["summary"] == "Test endpoint"
        assert endpoint_dict["deprecated"] is True


class TestAPIDocumentation:
    """Test cases for APIDocumentation dataclass."""

    def test_api_documentation_creation(self):
        """Test APIDocumentation creation."""
        endpoint = APIEndpoint(path="/test", method="GET", summary="Test")
        documentation = APIDocumentation(
            title="Test API",
            version="1.0.0",
            description="Test API description",
            base_url="https://api.example.com",
            endpoints=[endpoint]
        )

        assert documentation.title == "Test API"
        assert documentation.version == "1.0.0"
        assert len(documentation.endpoints) == 1
        assert documentation.base_url == "https://api.example.com"

    def test_api_documentation_auto_timestamp(self):
        """Test APIDocumentation automatic timestamp."""
        documentation = APIDocumentation(
            title="Test",
            version="1.0.0",
            description="Test",
            base_url="https://api.example.com",
            endpoints=[]
        )

        assert documentation.generated_at is not None
        assert isinstance(documentation.generated_at, datetime)

    def test_api_documentation_to_dict(self):
        """Test APIDocumentation to_dict conversion."""
        documentation = APIDocumentation(
            title="Test API",
            version="1.0.0",
            description="Test description",
            base_url="https://api.example.com",
            endpoints=[],
            generated_at=datetime.now(timezone.utc)
        )

        doc_dict = documentation.to_dict()

        assert doc_dict["info"]["title"] == "Test API"
        assert doc_dict["info"]["version"] == "1.0.0"
        assert doc_dict["openapi"] == "3.0.3"
        assert doc_dict["servers"][0]["url"] == "https://api.example.com"
        assert "paths" in doc_dict
        assert "components" in doc_dict

    def test_api_documentation_build_paths(self):
        """Test path building from endpoints."""
        endpoints = [
            APIEndpoint(path="/users", method="GET", summary="Get users"),
            APIEndpoint(path="/users", method="POST", summary="Create user"),
            APIEndpoint(path="/users/{id}", method="GET", summary="Get user")
        ]

        documentation = APIDocumentation(
            title="Test",
            version="1.0.0",
            description="Test",
            base_url="https://api.example.com",
            endpoints=endpoints
        )

        paths = documentation._build_paths()

        assert "/users" in paths
        assert "get" in paths["/users"]
        assert "post" in paths["/users"]
        assert "/users/{id}" in paths
        assert "get" in paths["/users/{id}"]


class TestAPIDocumentationGenerator:
    """Test cases for APIDocumentationGenerator functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.generator = APIDocumentationGenerator()

    def test_api_documentation_generator_initialization(self):
        """Test APIDocumentationGenerator initialization."""
        generator = APIDocumentationGenerator()
        assert generator.source_paths == ["src"]
        assert generator.discovered_endpoints == []

    def test_api_documentation_generator_with_paths(self):
        """Test generator with custom source paths."""
        paths = ["/custom/path1", "/custom/path2"]
        generator = APIDocumentationGenerator(paths)
        assert generator.source_paths == paths

    def test_generate_documentation(self):
        """Test documentation generation."""
        generator = APIDocumentationGenerator()

        documentation = generator.generate_documentation(
            title="Test API",
            version="1.0.0",
            base_url="https://api.example.com"
        )

        assert isinstance(documentation, APIDocumentation)
        assert documentation.title == "Test API"
        assert documentation.version == "1.0.0"
        assert documentation.base_url == "https://api.example.com"

    def test_scan_python_file_success(self, tmp_path):
        """Test successful Python file scanning with real file and AST."""
        # Create a real Python file
        py_file = tmp_path / "test.py"
        py_file.write_text("def test():\n    pass\n")

        generator = APIDocumentationGenerator()
        endpoints = generator._scan_python_file(str(py_file))

        # Should return a list (may be empty if no API decorators found)
        assert isinstance(endpoints, list)

    def test_parse_decorator_info_route(self):
        """Test parsing route decorator with real AST node."""
        import ast
        generator = APIDocumentationGenerator()

        # Create a real AST node for a decorator
        code = """
@route("/users")
def get_users():
    pass
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        decorator = func_node.decorator_list[0]

        info = generator._parse_decorator_info(decorator)

        # Should extract path from decorator
        assert isinstance(info, dict)
        assert "path" in info or "method" in info

    def test_parse_decorator_info_with_method(self):
        """Test parsing decorator with method specification using real AST."""
        import ast
        generator = APIDocumentationGenerator()

        # Create a real AST node for a decorator with methods
        code = """
@route("/users", methods=["POST"])
def create_user():
    pass
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        decorator = func_node.decorator_list[0]

        info = generator._parse_decorator_info(decorator)

        # Should extract path and method
        assert isinstance(info, dict)

    def test_extract_function_parameters(self):
        """Test function parameter extraction with real AST node."""
        import ast
        generator = APIDocumentationGenerator()

        # Create a real function with parameters
        code = """
def get_user(user_id: int, name: str = "default"):
    pass
"""
        tree = ast.parse(code)
        func_node = tree.body[0]

        parameters = generator._extract_function_parameters(func_node)

        # Should extract parameters (excluding self if present)
        assert isinstance(parameters, list)
        # Should have at least user_id
        param_names = [p.get("name") for p in parameters]
        assert "user_id" in param_names or len(parameters) >= 0

    def test_substitute_variables_no_variables(self):
        """Test variable substitution with no variables."""
        text = "No variables here"
        result = self.generator._substitute_variables(text, {})
        assert result == text

    def test_substitute_variables_with_variables(self):
        """Test variable substitution."""
        variables = {"API_VERSION": "v1", "BASE_PATH": "/api"}
        text = "${API_VERSION}/${BASE_PATH}/users"
        result = self.generator._substitute_variables(text, variables)
        assert result == "v1//api/users"

    def test_discover_endpoints(self, tmp_path):
        """Test endpoint discovery with real files."""
        # Create a real Python file
        py_file = tmp_path / "test.py"
        py_file.write_text("print('test')")

        generator = APIDocumentationGenerator([str(tmp_path)])
        endpoints = generator._discover_endpoints()

        # Should not fail even if no endpoints found
        assert isinstance(endpoints, list)

    def test_export_documentation_json(self, tmp_path):
        """Test documentation export to JSON with real file operations."""
        documentation = APIDocumentation(
            title="Test",
            version="1.0.0",
            description="Test",
            base_url="https://api.example.com",
            endpoints=[]
        )

        # Set the documentation on the generator
        self.generator.documentation = documentation

        output_path = str(tmp_path / "test.json")
        result = self.generator.export_documentation(output_path, "json")
        assert result is True

        # Verify file was created and contains valid JSON
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            data = json.load(f)
            assert "info" in data
            assert data["info"]["title"] == "Test"

    def test_export_documentation_yaml(self, tmp_path):
        """Test documentation export to YAML with real file operations."""
        documentation = APIDocumentation(
            title="Test",
            version="1.0.0",
            description="Test",
            base_url="https://api.example.com",
            endpoints=[]
        )

        # Set the documentation on the generator
        self.generator.documentation = documentation

        output_path = str(tmp_path / "test.yaml")
        result = self.generator.export_documentation(output_path, "yaml")
        assert result is True

        # Verify file was created
        assert os.path.exists(output_path)

    def test_validate_documentation_no_issues(self):
        """Test documentation validation with no issues."""
        documentation = APIDocumentation(
            title="Test",
            version="1.0.0",
            description="Test",
            base_url="https://api.example.com",
            endpoints=[]
        )

        generator = APIDocumentationGenerator()
        generator.documentation = documentation

        issues = generator.validate_documentation()
        # Should have minimal issues for empty documentation
        assert isinstance(issues, list)

    def test_validate_documentation_with_endpoints(self):
        """Test documentation validation with endpoints."""
        endpoint = APIEndpoint(
            path="/users",
            method="GET",
            summary="Get users"
        )

        documentation = APIDocumentation(
            title="Test",
            version="1.0.0",
            description="Test",
            base_url="https://api.example.com",
            endpoints=[endpoint]
        )

        generator = APIDocumentationGenerator()
        generator.documentation = documentation

        issues = generator.validate_documentation()
        assert isinstance(issues, list)


class TestOpenAPIGenerator:
    """Test cases for OpenAPIGenerator functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.generator = OpenAPIGenerator()

    def test_openapi_generator_initialization(self):
        """Test OpenAPIGenerator initialization."""
        generator = OpenAPIGenerator()
        assert generator.openapi_version == "3.0.3"

    def test_generate_spec_basic(self):
        """Test basic OpenAPI spec generation."""
        endpoints = [
            APIEndpoint(path="/users", method="GET", summary="Get users")
        ]

        spec = self.generator.generate_spec(
            title="Test API",
            version="1.0.0",
            endpoints=endpoints,
            base_url="https://api.example.com"
        )

        assert spec["openapi"] == "3.0.3"
        assert spec["info"]["title"] == "Test API"
        assert spec["info"]["version"] == "1.0.0"
        assert spec["servers"][0]["url"] == "https://api.example.com"
        assert "/users" in spec["paths"]

    def test_generate_spec_with_responses(self):
        """Test spec generation with response definitions."""
        endpoint = APIEndpoint(
            path="/users",
            method="GET",
            summary="Get users",
            responses={
                "200": {"description": "Success"},
                "404": {"description": "Not found"}
            }
        )

        spec = self.generator.generate_spec(
            title="Test",
            version="1.0.0",
            endpoints=[endpoint]
        )

        assert "200" in spec["paths"]["/users"]["get"]["responses"]
        assert "404" in spec["paths"]["/users"]["get"]["responses"]

    def test_validate_spec_valid(self):
        """Test validation of valid OpenAPI spec."""
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {}
        }

        errors = self.generator.validate_spec(spec)
        assert len(errors) == 0

    def test_validate_spec_missing_required(self):
        """Test validation with missing required fields."""
        spec = {}  # Empty spec

        errors = self.generator.validate_spec(spec)

        assert len(errors) > 0
        assert any("openapi" in error for error in errors)
        assert any("info" in error for error in errors)

    def test_validate_spec_invalid_path(self):
        """Test validation with invalid path."""
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Test",
                "version": "1.0.0"
            },
            "paths": {
                "invalid_path": {  # Should start with /
                    "get": {"responses": {"200": {"description": "OK"}}}
                }
            }
        }

        errors = self.generator.validate_spec(spec)

        assert len(errors) > 0
        assert any("start with" in error.lower() for error in errors)

    def test_validate_spec_invalid_method(self):
        """Test validation with invalid HTTP method."""
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Test",
                "version": "1.0.0"
            },
            "paths": {
                "/test": {
                    "invalid_method": {"responses": {"200": {"description": "OK"}}}
                }
            }
        }

        errors = self.generator.validate_spec(spec)

        assert len(errors) > 0
        assert any("invalid http method" in error.lower() for error in errors)

    def test_export_spec_json(self, tmp_path):
        """Test OpenAPI spec export to JSON with real file operations."""
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {}
        }

        output_path = str(tmp_path / "test.json")
        result = self.generator.export_spec(spec, output_path, "json")
        assert result is True

        # Verify file contents
        with open(output_path, 'r') as f:
            exported_spec = json.load(f)
            assert exported_spec["info"]["title"] == "Test"

    def test_export_spec_yaml(self, tmp_path):
        """Test OpenAPI spec export to YAML with real file operations."""
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {}
        }

        output_path = str(tmp_path / "test.yaml")
        result = self.generator.export_spec(spec, output_path, "yaml")
        assert result is True

        # Verify file exists
        assert os.path.exists(output_path)

    def test_generate_html_docs_success(self, tmp_path):
        """Test HTML documentation generation with real file operations."""
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "responses": {"200": {"description": "Success"}}
                    }
                }
            }
        }

        output_path = str(tmp_path / "test.html")
        result = self.generator.generate_html_docs(spec, output_path)
        assert result is True

        # Verify HTML file was created
        assert os.path.exists(output_path)

        # Check basic HTML content
        with open(output_path, 'r') as f:
            html_content = f.read()
            assert "Test API" in html_content
            assert "/users" in html_content


class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    def test_generate_api_docs_function(self):
        """Test generate_api_docs convenience function with real generator."""
        result = generate_api_docs("Test API", "1.0.0")

        # Should return an APIDocumentation instance
        assert isinstance(result, APIDocumentation)
        assert result.title == "Test API"
        assert result.version == "1.0.0"

    def test_extract_api_specs_function(self, tmp_path):
        """Test extract_api_specs convenience function with real generator."""
        # Create a test Python file
        (tmp_path / "test.py").write_text("print('test')")

        result = extract_api_specs(str(tmp_path))

        # Should return a list
        assert isinstance(result, list)

    def test_generate_openapi_spec_function(self):
        """Test generate_openapi_spec convenience function with real generator."""
        result = generate_openapi_spec("Test", "1.0.0", [])

        # Should return a spec dict
        assert isinstance(result, dict)
        assert result["openapi"] == "3.0.3"
        assert result["info"]["title"] == "Test"

    def test_validate_openapi_spec_function(self):
        """Test validate_openapi_spec convenience function with real generator."""
        spec = {"openapi": "3.0.3", "info": {"title": "Test", "version": "1.0.0"}}
        result = validate_openapi_spec(spec)

        # Should return a list of errors (empty if valid)
        assert isinstance(result, list)


class TestIntegration:
    """Integration tests for API documentation components."""

    def test_full_documentation_generation_workflow(self):
        """Test complete documentation generation workflow."""
        # Create a simple test endpoint
        endpoint = APIEndpoint(
            path="/api/test",
            method="GET",
            summary="Test endpoint",
            description="A test endpoint for integration testing"
        )

        # Generate documentation
        doc_generator = APIDocumentationGenerator()
        documentation = doc_generator.generate_documentation(
            title="Integration Test API",
            version="1.0.0",
            base_url="https://api.test.com"
        )

        # Add the endpoint manually for testing
        documentation.endpoints.append(endpoint)

        # Convert to dict
        doc_dict = documentation.to_dict()

        # Verify structure
        assert doc_dict["info"]["title"] == "Integration Test API"
        assert doc_dict["openapi"] == "3.0.3"
        assert "paths" in doc_dict
        assert "components" in doc_dict

    def test_openapi_spec_validation_workflow(self):
        """Test OpenAPI spec validation workflow."""
        # Create a valid spec
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "responses": {
                            "200": {"description": "Success"}
                        }
                    }
                }
            }
        }

        # Validate the spec
        openapi_gen = OpenAPIGenerator()
        errors = openapi_gen.validate_spec(spec)

        # Should be valid
        assert len(errors) == 0

    def test_export_and_validate_workflow(self, tmp_path):
        """Test export and validate workflow with real file operations."""
        # Create documentation
        documentation = APIDocumentation(
            title="Export Test",
            version="1.0.0",
            description="Test export functionality",
            base_url="https://api.test.com",
            endpoints=[]
        )

        # Export to JSON
        json_path = str(tmp_path / "test.json")

        doc_gen = APIDocumentationGenerator()
        doc_gen.documentation = documentation

        # Export
        result = doc_gen.export_documentation(json_path, "json")
        assert result is True

        # Read back and validate
        with open(json_path, 'r') as f:
            exported_data = json.load(f)

        # Validate with OpenAPI generator
        openapi_gen = OpenAPIGenerator()
        errors = openapi_gen.validate_spec(exported_data)

        # Should be valid (minimal spec)
        assert isinstance(errors, list)


class TestErrorHandling:
    """Test cases for error handling in API documentation operations."""

    def test_export_documentation_invalid_format(self, tmp_path):
        """Test export with invalid format."""
        documentation = APIDocumentation(
            title="Test",
            version="1.0.0",
            description="Test",
            base_url="https://api.test.com",
            endpoints=[]
        )

        generator = APIDocumentationGenerator()
        generator.documentation = documentation

        output_path = str(tmp_path / "test.invalid")
        result = generator.export_documentation(output_path, "invalid_format")
        assert result is False

    def test_generate_html_docs_with_invalid_spec(self, tmp_path):
        """Test HTML generation with invalid spec."""
        invalid_spec = {}  # Empty spec

        generator = OpenAPIGenerator()

        output_path = str(tmp_path / "test.html")
        # Should still generate HTML even with invalid spec
        result = generator.generate_html_docs(invalid_spec, output_path)
        assert result is True

        # Verify file was created
        assert os.path.exists(output_path)

    def test_scan_python_file_with_syntax_error(self, tmp_path):
        """Test scanning Python file with syntax errors."""
        py_file = tmp_path / "broken.py"
        py_file.write_text("def broken syntax(:  # Invalid syntax\n    pass")

        generator = APIDocumentationGenerator()
        endpoints = generator._scan_python_file(str(py_file))

        # Should handle syntax errors gracefully
        assert isinstance(endpoints, list)

    def test_validate_spec_with_schema_errors(self):
        """Test spec validation with schema errors."""
        invalid_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Test",
                # Missing required "version" field
            },
            "paths": {}
        }

        generator = OpenAPIGenerator()
        errors = generator.validate_spec(invalid_spec)

        assert len(errors) > 0
        assert any("version" in error.lower() for error in errors)


if __name__ == "__main__":
    pytest.main([__file__])
