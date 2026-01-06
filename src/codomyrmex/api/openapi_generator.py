"""
Unified OpenAPI Specification Generator for Codomyrmex API Module.

This module provides comprehensive OpenAPI/Swagger specification generation
from multiple sources:
- Code analysis and documentation extraction
- REST API instances
- GraphQL API instances
- Versioned endpoints
"""

import json
import os
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Dict, List, Union

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Import from standardization submodule
try:
    from .standardization.rest_api import RESTAPI, APIEndpoint as StandardizationAPIEndpoint, HTTPMethod
    from .standardization.graphql_api import GraphQLAPI, GraphQLSchema, GraphQLObjectType, GraphQLField
    from .standardization.api_versioning import APIVersionManager, APIVersion
except ImportError:
    # Handle case where standardization module isn't available yet
    RESTAPI = None
    StandardizationAPIEndpoint = None
    HTTPMethod = None
    GraphQLAPI = None
    GraphQLSchema = None
    GraphQLObjectType = None
    GraphQLField = None
    APIVersionManager = None
    APIVersion = None


@dataclass
class APISchema:
    """API schema definition for documentation generation."""

    name: str
    schema_type: str
    properties: dict[str, Any] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)
    example: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert schema to OpenAPI format."""
        schema = {"type": self.schema_type, "properties": self.properties}

        if self.required:
            schema["required"] = self.required

        if self.example:
            schema["example"] = self.example

        return schema


@dataclass
class OpenAPISpecification:
    """OpenAPI specification container."""
    spec: Dict[str, Any] = field(default_factory=dict)
    version: str = "3.0.3"

    def to_dict(self) -> Dict[str, Any]:
        """Get the specification as a dictionary."""
        return self.spec

    def to_json(self, indent: int = 2) -> str:
        """Get the specification as JSON."""
        return json.dumps(self.spec, indent=indent)

    def to_yaml(self) -> str:
        """Get the specification as YAML."""
        try:
            import yaml
            return yaml.dump(self.spec, default_flow_style=False)
        except ImportError:
            raise ImportError("PyYAML is required for YAML output")

    def save_to_file(self, filepath: str, format: str = "json") -> None:
        """
        Save the specification to a file.

        Args:
            filepath: Path to save the file
            format: File format ('json' or 'yaml')
        """
        if format.lower() == "json":
            with open(filepath, 'w') as f:
                f.write(self.to_json())
        elif format.lower() == "yaml":
            with open(filepath, 'w') as f:
                f.write(self.to_yaml())
        else:
            raise ValueError(f"Unsupported format: {format}")


class DocumentationOpenAPIGenerator:
    """
    OpenAPI 3.0 specification generator from code analysis/documentation.

    This generator creates OpenAPI specs from endpoint lists and documentation.
    Used primarily by the documentation submodule.
    """

    def __init__(self):
        """Initialize the OpenAPI generator."""
        self.openapi_version = "3.0.3"

    def generate_spec(
        self,
        title: str,
        version: str,
        endpoints: list[Any],
        base_url: str = "http://localhost:8000",
    ) -> dict[str, Any]:
        """
        Generate OpenAPI 3.0 specification from endpoint list.

        Args:
            title: API title
            version: API version
            endpoints: List of API endpoints
            base_url: Base API URL

        Returns:
            Dict containing OpenAPI specification
        """
        spec = {
            "openapi": self.openapi_version,
            "info": {
                "title": title,
                "version": version,
                "description": f"Auto-generated OpenAPI specification for {title}",
            },
            "servers": [{"url": base_url}],
            "paths": {},
            "components": {"schemas": {}, "securitySchemes": {}},
        }

        # Process endpoints
        for endpoint in endpoints:
            endpoint_dict = (
                endpoint.to_dict() if hasattr(endpoint, "to_dict") else endpoint
            )

            path = endpoint_dict.get("path", "/")
            method = endpoint_dict.get("method", "GET").lower()

            if path not in spec["paths"]:
                spec["paths"][path] = {}

            spec["paths"][path][method] = {
                "summary": endpoint_dict.get("summary", ""),
                "description": endpoint_dict.get("description", ""),
                "parameters": endpoint_dict.get("parameters", []),
                "responses": endpoint_dict.get(
                    "responses", {"200": {"description": "Success"}}
                ),
            }

            # Add request body if present
            if "requestBody" in endpoint_dict and endpoint_dict["requestBody"]:
                spec["paths"][path][method]["requestBody"] = endpoint_dict[
                    "requestBody"
                ]

            # Add security if present
            if endpoint_dict.get("security"):
                spec["paths"][path][method]["security"] = endpoint_dict["security"]

        # Add default schemas
        spec["components"]["schemas"] = self._get_default_schemas()

        # Add security schemes
        spec["components"]["securitySchemes"] = self._get_default_security_schemes()

        return spec

    def _get_default_schemas(self) -> dict[str, Any]:
        """Get default OpenAPI schemas."""
        return {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "description": "Error type"},
                    "message": {"type": "string", "description": "Error message"},
                    "code": {"type": "integer", "description": "Error code"},
                },
                "required": ["error", "message"],
            },
            "Success": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "description": "Success status"},
                    "data": {"type": "object", "description": "Response data"},
                    "message": {"type": "string", "description": "Success message"},
                },
                "required": ["success"],
            },
        }

    def _get_default_security_schemes(self) -> dict[str, Any]:
        """Get default security schemes."""
        return {
            "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
            "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
            "BasicAuth": {"type": "http", "scheme": "basic"},
        }

    def validate_spec(self, spec: dict[str, Any]) -> list[str]:
        """
        Validate OpenAPI specification.

        Args:
            spec: OpenAPI specification dictionary

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required fields
        if "openapi" not in spec:
            errors.append("Missing required field: openapi")

        if "info" not in spec:
            errors.append("Missing required field: info")
        elif not isinstance(spec["info"], dict):
            errors.append("info must be an object")
        else:
            if "title" not in spec["info"]:
                errors.append("Missing required field: info.title")
            if "version" not in spec["info"]:
                errors.append("Missing required field: info.version")

        if "paths" not in spec:
            errors.append("Missing required field: paths")

        # Validate paths
        if "paths" in spec and isinstance(spec["paths"], dict):
            for path, methods in spec["paths"].items():
                if not path.startswith("/"):
                    errors.append(f"Path must start with '/': {path}")

                if not isinstance(methods, dict):
                    errors.append(f"Path methods must be an object: {path}")
                    continue

                for method, operation in methods.items():
                    if method.lower() not in [
                        "get",
                        "post",
                        "put",
                        "delete",
                        "patch",
                        "options",
                        "head",
                    ]:
                        errors.append(f"Invalid HTTP method: {method}")

                    if not isinstance(operation, dict):
                        errors.append(f"Operation must be an object: {path} {method}")
                        continue

                    if "responses" not in operation:
                        errors.append(
                            f"Missing responses in operation: {path} {method}"
                        )

        return errors

    def export_spec(
        self, spec: dict[str, Any], output_path: str, format: str = "json"
    ) -> bool:
        """
        Export OpenAPI specification to file.

        Args:
            spec: OpenAPI specification
            output_path: Output file path
            format: Export format (json, yaml)

        Returns:
            bool: True if export successful
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if format.lower() == "json":
                with open(output_path, "w") as f:
                    json.dump(spec, f, indent=2)

            elif format.lower() == "yaml":
                import yaml

                with open(output_path, "w") as f:
                    yaml.dump(spec, f, default_flow_style=False)

            else:
                logger.error(f"Unsupported format: {format}")
                return False

            logger.info(f"OpenAPI spec exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export OpenAPI spec: {e}")
            return False

    def generate_html_docs(self, spec: dict[str, Any], output_path: str) -> bool:
        """
        Generate HTML documentation from OpenAPI spec.

        Args:
            spec: OpenAPI specification
            output_path: Output HTML file path

        Returns:
            bool: True if generation successful
        """
        try:
            html_content = self._generate_html_content(spec)

            with open(output_path, "w") as f:
                f.write(html_content)

            logger.info(f"HTML documentation generated: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate HTML docs: {e}")
            return False

    def _generate_html_content(self, spec: dict[str, Any]) -> str:
        """Generate HTML content for API documentation."""
        title = spec.get("info", {}).get("title", "API Documentation")
        version = spec.get("info", {}).get("version", "1.0.0")
        description = spec.get("info", {}).get("description", "")

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title} - API Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .endpoint {{ background: #ffffff; border: 1px solid #dee2e6; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .method {{ font-weight: bold; padding: 5px 10px; border-radius: 3px; color: white; }}
        .method.GET {{ background: #28a745; }}
        .method.POST {{ background: #007bff; }}
        .method.PUT {{ background: #ffc107; color: black; }}
        .method.DELETE {{ background: #dc3545; }}
        .parameters {{ margin-top: 10px; }}
        .parameter {{ background: #f8f9fa; padding: 5px; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p><strong>Version:</strong> {version}</p>
        <p>{description}</p>
    </div>

    <h2>API Endpoints</h2>
"""

        paths = spec.get("paths", {})
        for path, methods in paths.items():
            for method, operation in methods.items():
                method_upper = method.upper()
                html += f"""
    <div class="endpoint">
        <span class="method {method_upper}">{method_upper}</span>
        <strong>{path}</strong>
        <p>{operation.get('summary', '')}</p>
        <p>{operation.get('description', '')}</p>
"""

                # Parameters
                parameters = operation.get("parameters", [])
                if parameters:
                    html += '<div class="parameters"><strong>Parameters:</strong>'
                    for param in parameters:
                        html += f'<div class="parameter">{param.get("name", "")}: {param.get("description", "")}</div>'
                    html += "</div>"

                html += "</div>"

        html += """
</body>
</html>"""

        return html


class StandardizationOpenAPIGenerator:
    """
    Generator for OpenAPI specifications from REST/GraphQL API instances.

    This generator creates OpenAPI specs from API framework instances.
    Used primarily by the standardization submodule.
    """

    def __init__(self, title: str = "Codomyrmex API", version: str = "1.0.0",
                 description: str = "API for Codomyrmex", base_url: str = "/api"):
        """
        Initialize the OpenAPI generator.

        Args:
            title: API title
            version: API version
            description: API description
            base_url: Base URL for the API
        """
        self.title = title
        self.version = version
        self.description = description
        self.base_url = base_url.rstrip('/')
        self.spec = OpenAPISpecification()

        # Initialize basic OpenAPI structure
        self.spec.spec = {
            "openapi": self.spec.version,
            "info": {
                "title": title,
                "version": version,
                "description": description
            },
            "paths": {},
            "components": {
                "schemas": {},
                "responses": {},
                "parameters": {}
            },
            "tags": []
        }

        logger.info(f"OpenAPI Generator initialized: {title} v{version}")

    def add_rest_api(self, api: RESTAPI) -> None:
        """
        Add a REST API to the specification.

        Args:
            api: REST API instance
        """
        if RESTAPI is None:
            raise ImportError("RESTAPI class not available. Ensure standardization module is properly imported.")

        for endpoint in api.get_endpoints():
            self._add_rest_endpoint(endpoint)

        # Add server information
        self.spec.spec["servers"] = [{
            "url": self.base_url,
            "description": f"{api.title} v{api.version}"
        }]

        logger.debug(f"Added REST API with {len(api.get_endpoints())} endpoints")

    def add_graphql_api(self, api: GraphQLAPI) -> None:
        """
        Add a GraphQL API to the specification.

        Args:
            api: GraphQL API instance
        """
        if GraphQLAPI is None:
            raise ImportError("GraphQLAPI class not available. Ensure standardization module is properly imported.")

        # Add GraphQL endpoint
        graphql_path = "/graphql"
        self.spec.spec["paths"][graphql_path] = {
            "post": {
                "summary": "Execute GraphQL query",
                "description": "Execute a GraphQL query or mutation",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/GraphQLRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "GraphQL response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/GraphQLResponse"
                                }
                            }
                        }
                    }
                },
                "tags": ["graphql"]
            }
        }

        # Add GraphQL schemas
        self._add_graphql_schemas(api.schema)

        # Add GraphQL playground endpoint
        playground_path = "/graphql/playground"
        self.spec.spec["paths"][playground_path] = {
            "get": {
                "summary": "GraphQL Playground",
                "description": "Interactive GraphQL playground interface",
                "responses": {
                    "200": {
                        "description": "GraphQL Playground HTML",
                        "content": {
                            "text/html": {
                                "schema": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                },
                "tags": ["graphql"]
            }
        }

        logger.debug("Added GraphQL API endpoints")

    def add_version_manager(self, version_manager: APIVersionManager) -> None:
        """
        Add version information to the specification.

        Args:
            version_manager: API version manager
        """
        if APIVersionManager is None:
            raise ImportError("APIVersionManager class not available. Ensure standardization module is properly imported.")

        # Add version parameter
        self.spec.spec["components"]["parameters"]["ApiVersion"] = {
            "name": "X-API-Version",
            "in": "header",
            "description": "API version to use",
            "required": False,
            "schema": {
                "type": "string",
                "enum": list(version_manager.versions.keys()),
                "default": version_manager.default_version
            }
        }

        # Add version information to info
        version_info = version_manager.get_version_info()
        self.spec.spec["info"]["x-api-versions"] = version_info

        logger.debug(f"Added version information for {len(version_manager.versions)} versions")

    def _add_rest_endpoint(self, endpoint: StandardizationAPIEndpoint) -> None:
        """
        Add a REST endpoint to the specification.

        Args:
            endpoint: API endpoint
        """
        path = endpoint.path
        method = endpoint.method.value.lower()

        if path not in self.spec.spec["paths"]:
            self.spec.spec["paths"][path] = {}

        operation = {
            "summary": endpoint.summary or f"{method.upper()} {path}",
            "description": endpoint.description or "",
            "responses": {}
        }

        # Add parameters
        if endpoint.parameters:
            operation["parameters"] = endpoint.parameters

        # Add request body
        if endpoint.request_body:
            operation["requestBody"] = endpoint.request_body

        # Add responses
        if endpoint.responses:
            operation["responses"] = endpoint.responses
        else:
            # Default responses
            operation["responses"]["200"] = {
                "description": "Successful response"
            }
            operation["responses"]["400"] = {
                "description": "Bad request"
            }
            operation["responses"]["500"] = {
                "description": "Internal server error"
            }

        # Add tags
        if endpoint.tags:
            operation["tags"] = endpoint.tags

        self.spec.spec["paths"][path][method] = operation

    def _add_graphql_schemas(self, schema: GraphQLSchema) -> None:
        """
        Add GraphQL schemas to the OpenAPI specification.

        Args:
            schema: GraphQL schema
        """
        components = self.spec.spec["components"]

        # Add GraphQL request/response schemas
        components["schemas"]["GraphQLRequest"] = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "GraphQL query string"
                },
                "variables": {
                    "type": "object",
                    "description": "Query variables",
                    "additionalProperties": True
                },
                "operationName": {
                    "type": "string",
                    "description": "Operation name"
                }
            },
            "required": ["query"]
        }

        components["schemas"]["GraphQLResponse"] = {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Query result data",
                    "additionalProperties": True
                },
                "errors": {
                    "type": "array",
                    "items": {
                        "$ref": "#/components/schemas/GraphQLError"
                    }
                }
            }
        }

        components["schemas"]["GraphQLError"] = {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Error message"
                },
                "locations": {
                    "type": "array",
                    "items": {
                        "$ref": "#/components/schemas/GraphQLLocation"
                    }
                },
                "path": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        }

        components["schemas"]["GraphQLLocation"] = {
            "type": "object",
            "properties": {
                "line": {"type": "integer"},
                "column": {"type": "integer"}
            }
        }

        # Add GraphQL type schemas
        for type_name, type_def in schema.types.items():
            self._convert_graphql_type_to_openapi(type_name, type_def)

    def _convert_graphql_type_to_openapi(self, name: str, graphql_type: GraphQLObjectType) -> None:
        """
        Convert a GraphQL type to OpenAPI schema.

        Args:
            name: Type name
            graphql_type: GraphQL type definition
        """
        schema = {
            "type": "object",
            "properties": {}
        }

        if graphql_type.description:
            schema["description"] = graphql_type.description

        for field_name, field in graphql_type.fields.items():
            field_schema = self._convert_graphql_field_to_openapi(field)
            schema["properties"][field_name] = field_schema

        self.spec.spec["components"]["schemas"][name] = schema

    def _convert_graphql_field_to_openapi(self, field: GraphQLField) -> Dict[str, Any]:
        """
        Convert a GraphQL field to OpenAPI schema.

        Args:
            field: GraphQL field

        Returns:
            OpenAPI field schema
        """
        if isinstance(field.type, str):
            # Built-in GraphQL type
            type_mapping = {
                "String": {"type": "string"},
                "Int": {"type": "integer"},
                "Float": {"type": "number"},
                "Boolean": {"type": "boolean"},
                "ID": {"type": "string"}
            }

            schema = type_mapping.get(field.type, {"type": "string"})
        else:
            # Custom type reference
            schema = {"$ref": f"#/components/schemas/{field.type.name}"}

        if field.description:
            schema["description"] = field.description

        if field.required:
            # This would be handled at the object level
            pass

        return schema

    def add_security_schemes(self, schemes: Dict[str, Dict[str, Any]]) -> None:
        """
        Add security schemes to the specification.

        Args:
            schemes: Security scheme definitions
        """
        if "securitySchemes" not in self.spec.spec["components"]:
            self.spec.spec["components"]["securitySchemes"] = {}

        self.spec.spec["components"]["securitySchemes"].update(schemes)

    def add_global_responses(self, responses: Dict[str, Dict[str, Any]]) -> None:
        """
        Add global response definitions.

        Args:
            responses: Response definitions
        """
        self.spec.spec["components"]["responses"].update(responses)

    def add_tags(self, tags: List[Dict[str, str]]) -> None:
        """
        Add tag definitions.

        Args:
            tags: Tag definitions
        """
        self.spec.spec["tags"].extend(tags)

    def set_external_docs(self, url: str, description: str = "Find out more about this API") -> None:
        """
        Set external documentation.

        Args:
            url: Documentation URL
            description: Documentation description
        """
        self.spec.spec["externalDocs"] = {
            "description": description,
            "url": url
        }

    def validate_spec(self) -> List[str]:
        """
        Validate the OpenAPI specification.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Basic validation
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            if field not in self.spec.spec:
                errors.append(f"Missing required field: {field}")

        if "title" not in self.spec.spec["info"]:
            errors.append("Missing required field: info.title")

        if "version" not in self.spec.spec["info"]:
            errors.append("Missing required field: info.version")

        # Check paths
        if self.spec.spec.get("paths"):
            for path, methods in self.spec.spec["paths"].items():
                if not isinstance(methods, dict):
                    errors.append(f"Invalid path definition: {path}")
                    continue

                for method, operation in methods.items():
                    if method not in ["get", "post", "put", "delete", "patch", "options", "head"]:
                        errors.append(f"Invalid HTTP method: {method} for path {path}")

                    if "responses" not in operation:
                        errors.append(f"Missing responses for {method.upper()} {path}")

        return errors

    def generate_spec(self) -> OpenAPISpecification:
        """
        Generate the final OpenAPI specification.

        Returns:
            OpenAPI specification
        """
        # Add generation metadata
        self.spec.spec["info"]["x-generated-at"] = datetime.now().isoformat()
        self.spec.spec["info"]["x-generator"] = "Codomyrmex OpenAPI Generator"

        # Validate before returning
        errors = self.validate_spec()
        if errors:
            logger.warning(f"OpenAPI specification validation errors: {errors}")

        return self.spec


# Convenience functions for documentation module
def generate_openapi_spec(
    title: str,
    version: str,
    endpoints: list[Any],
    base_url: str = "http://localhost:8000",
) -> dict[str, Any]:
    """
    Convenience function to generate OpenAPI specification from endpoints.

    Args:
        title: API title
        version: API version
        endpoints: List of API endpoints
        base_url: Base API URL

    Returns:
        Dict containing OpenAPI specification
    """
    generator = DocumentationOpenAPIGenerator()
    return generator.generate_spec(title, version, endpoints, base_url)


def validate_openapi_spec(spec: dict[str, Any]) -> list[str]:
    """
    Convenience function to validate OpenAPI specification.

    Args:
        spec: OpenAPI specification dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    generator = DocumentationOpenAPIGenerator()
    return generator.validate_spec(spec)


# Convenience functions for standardization module
def create_openapi_generator(title: str = "Codomyrmex API", version: str = "1.0.0",
                             description: str = "API for Codomyrmex") -> StandardizationOpenAPIGenerator:
    """
    Create a new OpenAPI generator for standardization.

    Args:
        title: API title
        version: API version
        description: API description

    Returns:
        StandardizationOpenAPIGenerator instance
    """
    return StandardizationOpenAPIGenerator(title=title, version=version, description=description)


def create_openapi_from_rest_api(api: RESTAPI) -> OpenAPISpecification:
    """
    Create OpenAPI spec from a REST API.

    Args:
        api: REST API instance

    Returns:
        OpenAPI specification
    """
    if RESTAPI is None:
        raise ImportError("RESTAPI class not available. Ensure standardization module is properly imported.")

    generator = StandardizationOpenAPIGenerator(
        title=api.title,
        version=api.version,
        description=api.description
    )
    generator.add_rest_api(api)
    return generator.generate_spec()


def create_openapi_from_graphql_api(api: GraphQLAPI) -> OpenAPISpecification:
    """
    Create OpenAPI spec from a GraphQL API.

    Args:
        api: GraphQL API instance

    Returns:
        OpenAPI specification
    """
    if GraphQLAPI is None:
        raise ImportError("GraphQLAPI class not available. Ensure standardization module is properly imported.")

    generator = StandardizationOpenAPIGenerator(
        title="GraphQL API",
        version="1.0.0",
        description="GraphQL API endpoint"
    )
    generator.add_graphql_api(api)
    return generator.generate_spec()

