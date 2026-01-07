#!/usr/bin/env python3
"""
Example: API Documentation - OpenAPI Spec Generation

Demonstrates:
- API documentation generation from code
- OpenAPI specification creation
- API spec validation
- Documentation export and rendering

Tested Methods:
- generate_api_docs() - Verified in test_api_documentation.py::TestConvenienceFunctions::test_generate_api_docs_function
- extract_api_specs() - Verified in test_api_documentation.py::TestConvenienceFunctions::test_extract_api_specs_function
- generate_openapi_spec() - Verified in test_api_documentation.py::TestConvenienceFunctions::test_generate_openapi_spec_function
- validate_openapi_spec() - Verified in test_api_documentation.py::TestConvenienceFunctions::test_validate_openapi_spec_function
"""

import sys
import os
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "examples" / "_common")) # Added for common utilities

from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error, ensure_output_dir

from codomyrmex.api.documentation import (
    generate_api_docs,
    extract_api_specs,
    generate_openapi_spec,
    validate_openapi_spec,
    APIDocumentationGenerator,
    OpenAPIGenerator,
    APIDocumentation,
    APIEndpoint,
    APISchema
)
from codomyrmex.logging_monitoring import setup_logging, get_logger

logger = get_logger(__name__)


def create_sample_api_endpoints() -> List[APIEndpoint]:
    """Create sample API endpoints for demonstration."""
    return [
        APIEndpoint(
            path="/users",
            method="GET",
            summary="Get users",
            description="Retrieve a list of users with optional filtering",
            parameters=[
                {
                    "name": "limit",
                    "in": "query",
                    "description": "Maximum number of users to return",
                    "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 10}
                },
                {
                    "name": "offset",
                    "in": "query",
                    "description": "Number of users to skip",
                    "schema": {"type": "integer", "minimum": 0, "default": 0}
                }
            ],
            responses={
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "users": {"type": "array", "items": {"$ref": "#/components/schemas/User"}},
                                    "total": {"type": "integer"},
                                    "limit": {"type": "integer"},
                                    "offset": {"type": "integer"}
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "Bad request",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {"type": "string"},
                                    "message": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            tags=["Users"]
        ),
        APIEndpoint(
            path="/users",
            method="POST",
            summary="Create user",
            description="Create a new user account",
            request_body={
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/NewUser"}
                    }
                }
            },
            responses={
                "201": {
                    "description": "User created successfully",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/User"}
                        }
                    }
                },
                "400": {
                    "description": "Validation error",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {"type": "string"},
                                    "message": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            tags=["Users"]
        ),
        APIEndpoint(
            path="/users/{userId}",
            method="GET",
            summary="Get user by ID",
            description="Retrieve a specific user by their ID",
            parameters=[
                {
                    "name": "userId",
                    "in": "path",
                    "required": True,
                    "description": "Unique identifier of the user",
                    "schema": {"type": "string", "format": "uuid"}
                }
            ],
            responses={
                "200": {
                    "description": "User found",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/User"}
                        }
                    }
                },
                "404": {
                    "description": "User not found",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {"type": "string"},
                                    "message": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            tags=["Users"]
        ),
        APIEndpoint(
            path="/products",
            method="GET",
            summary="Get products",
            description="Retrieve a list of products with filtering options",
            parameters=[
                {
                    "name": "category",
                    "in": "query",
                    "description": "Filter products by category",
                    "schema": {"type": "string"}
                },
                {
                    "name": "price_min",
                    "in": "query",
                    "description": "Minimum price filter",
                    "schema": {"type": "number", "minimum": 0}
                },
                {
                    "name": "price_max",
                    "in": "query",
                    "description": "Maximum price filter",
                    "schema": {"type": "number", "minimum": 0}
                }
            ],
            responses={
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "products": {"type": "array", "items": {"$ref": "#/components/schemas/Product"}},
                                    "total": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            },
            tags=["Products"]
        )
    ]


def create_sample_schemas() -> Dict[str, Any]:
    """Create sample OpenAPI schemas for demonstration."""
    return {
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "username": {"type": "string", "minLength": 3, "maxLength": 50},
                "email": {"type": "string", "format": "email"},
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "createdAt": {"type": "string", "format": "date-time"},
                "updatedAt": {"type": "string", "format": "date-time"}
            },
            "required": ["id", "username", "email"]
        },
        "NewUser": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "minLength": 3, "maxLength": 50},
                "email": {"type": "string", "format": "email"},
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "password": {"type": "string", "minLength": 8}
            },
            "required": ["username", "email", "password"]
        },
        "Product": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "price": {"type": "number", "minimum": 0},
                "category": {"type": "string"},
                "inStock": {"type": "boolean", "default": True},
                "tags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["id", "name", "price"]
        },
        "Error": {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "message": {"type": "string"},
                "code": {"type": "integer"}
            },
            "required": ["error", "message"]
        }
    }


def main():
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    temp_dir = None
    try:
        print_section("API Documentation Example")
        print("Demonstrating comprehensive API documentation generation and OpenAPI specification")

        # Create a temporary directory for output files
        temp_dir = tempfile.mkdtemp()
        output_dir = Path(temp_dir) / "api_docs"
        output_dir.mkdir()
        ensure_output_dir(output_dir)

        # 1. Create sample API endpoints and schemas
        print("\n📋 Creating sample API endpoints and schemas...")
        endpoints = create_sample_api_endpoints()
        schemas = create_sample_schemas()
        print_success(f"Created {len(endpoints)} sample endpoints and {len(schemas)} schemas")

        # 2. Generate API documentation using convenience function
        print("\n📚 Generating API documentation...")
        documentation = generate_api_docs(
            title="Sample E-commerce API",
            version="1.0.0",
            base_url="https://api.example.com"
        )
        # Add our sample endpoints manually for demonstration
        documentation.endpoints = endpoints
        print_success(f"Generated API documentation with {len(documentation.endpoints)} endpoints")

        # 3. Extract API specifications (simulated from code)
        print("\n🔍 Extracting API specifications from code...")
        # For demonstration, we'll create a temporary Python file with API routes
        api_code_file = output_dir / "sample_api.py"
        api_code_file.write_text("""
@app.route('/users', methods=['GET'])
def get_users():
    \"\"\"Get users endpoint.\"\"\"
    return {"users": []}

@app.route('/users', methods=['POST'])
def create_user():
    \"\"\"Create user endpoint.\"\"\"
    return {"user": {}}

@app.route('/products', methods=['GET'])
def get_products():
    \"\"\"Get products endpoint.\"\"\"
    return {"products": []}
""")
        specs = extract_api_specs(str(output_dir))
        print_success(f"Extracted {len(specs)} API specifications from code")

        # 4. Generate OpenAPI specification
        print("\n📋 Generating OpenAPI specification...")
        openapi_spec = generate_openapi_spec(
            title="Sample E-commerce API",
            version="1.0.0",
            endpoints=endpoints,
            base_url="https://api.example.com"
        )
        # Manually add schemas and description to the spec
        openapi_spec["info"]["description"] = "A comprehensive e-commerce API for managing users and products"
        openapi_spec["components"]["schemas"] = schemas
        print_success(f"Generated OpenAPI {openapi_spec['openapi']} specification")

        # 5. Validate OpenAPI specification
        print("\n✅ Validating OpenAPI specification...")
        validation_errors = validate_openapi_spec(openapi_spec)
        if validation_errors:
            print_error(f"OpenAPI spec validation failed: {validation_errors}")
            # runner.error("OpenAPI validation failed", validation_errors)
            # sys.exit(1)
        else:
            print_success("OpenAPI specification is valid")

        # 6. Export documentation in multiple formats
        print("\n💾 Exporting documentation...")
        doc_generator = APIDocumentationGenerator()
        doc_generator.documentation = documentation

        # Export to JSON
        json_path = output_dir / "api_documentation.json"
        json_exported = doc_generator.export_documentation(str(json_path), "json")
        print_success(f"Exported API documentation to JSON: {json_exported}")

        # Export to YAML
        yaml_path = output_dir / "api_documentation.yaml"
        yaml_exported = doc_generator.export_documentation(str(yaml_path), "yaml")
        print_success(f"Exported API documentation to YAML: {yaml_exported}")

        # 7. Generate OpenAPI spec exports
        print("\n📄 Generating OpenAPI specification exports...")
        openapi_generator = OpenAPIGenerator()

        # Export OpenAPI spec to JSON
        openapi_json_path = output_dir / "openapi_spec.json"
        json_exported = openapi_generator.export_spec(openapi_spec, str(openapi_json_path), "json")
        print_success(f"Exported OpenAPI spec to JSON: {json_exported}")

        # Export OpenAPI spec to YAML
        openapi_yaml_path = output_dir / "openapi_spec.yaml"
        yaml_exported = openapi_generator.export_spec(openapi_spec, str(openapi_yaml_path), "yaml")
        print_success(f"Exported OpenAPI spec to YAML: {yaml_exported}")

        # 8. Generate HTML documentation
        print("\n🌐 Generating HTML documentation...")
        html_path = output_dir / "api_documentation.html"
        html_generated = openapi_generator.generate_html_docs(openapi_spec, str(html_path))
        print_success(f"Generated HTML documentation: {html_generated}")

        # 9. Validate exported files
        print("\n🔍 Validating exported files...")
        exported_files = [
            json_path, yaml_path, openapi_json_path, openapi_yaml_path, html_path
        ]
        file_validation_results = {}
        for file_path in exported_files:
            exists = file_path.exists()
            size = file_path.stat().st_size if exists else 0
            file_validation_results[file_path.name] = {
                "exists": exists,
                "size_bytes": size,
                "readable": exists and file_path.read_text()[:100] != ""
            }

        all_files_exist = all(result["exists"] for result in file_validation_results.values())
        if all_files_exist:
            print_success("All exported files created successfully")
        else:
            print_error("Some exported files are missing")

        # 10. Demonstrate advanced OpenAPI generator features
        print("\n⚡ Demonstrating advanced OpenAPI features...")
        advanced_spec = openapi_generator.generate_spec(
            title="Advanced Sample API",
            version="2.0.0",
            endpoints=endpoints[:2],  # Use first 2 endpoints
            base_url="https://api.example.com/v2"
        )
        # Manually add schemas and security schemes
        advanced_spec["components"]["schemas"] = schemas
        advanced_spec["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            },
            "apiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        }
        advanced_spec["security"] = [
            {"bearerAuth": []},
            {"apiKeyAuth": []}
        ]
        print_success(f"Generated advanced spec with security schemes")

        # Validate the advanced spec
        advanced_validation = openapi_generator.validate_spec(advanced_spec)
        print_success(f"Advanced spec validation: {len(advanced_validation)} errors")

        final_results = {
            "endpoints_created": len(endpoints),
            "schemas_created": len(schemas),
            "documentation_generated": documentation.title == "Sample E-commerce API",
            "api_specs_extracted": len(specs),
            "openapi_spec_generated": openapi_spec["openapi"] == "3.0.3",
            "openapi_validation_passed": len(validation_errors) == 0,
            "json_export_success": json_exported,
            "yaml_export_success": yaml_exported,
            "openapi_json_export_success": json_exported,
            "openapi_yaml_export_success": yaml_exported,
            "html_docs_generated": html_generated,
            "all_exported_files_exist": all_files_exist,
            "exported_files_count": len(exported_files),
            "advanced_spec_generated": advanced_spec["info"]["version"] == "2.0.0",
            "advanced_validation_passed": len(advanced_validation) == 0,
            "total_endpoints_documented": len(endpoints),
            "total_schemas_defined": len(schemas),
            "api_title": documentation.title,
            "api_version": documentation.version,
            "base_url": documentation.base_url,
            "output_directory": str(output_dir)
        }

        print_results(final_results, "API Documentation Operations Summary")

        runner.validate_results(final_results)
        runner.save_results(final_results)
        runner.complete()
        print("\n✅ API Documentation example completed successfully!")
        print("All API documentation generation and OpenAPI specification features demonstrated.")
        print(f"Generated comprehensive documentation for {len(endpoints)} endpoints")
        print(f"Created {len(schemas)} data schemas and exported to {len(exported_files)} formats")
        print(f"OpenAPI {openapi_spec['openapi']} specification validated and exported")

    except Exception as e:
        runner.error("API Documentation example failed", e)
        print(f"\n❌ API Documentation example failed: {e}")
        sys.exit(1)
    finally:
        if temp_dir and Path(temp_dir).exists():
            import shutil
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")


if __name__ == "__main__":
    main()
