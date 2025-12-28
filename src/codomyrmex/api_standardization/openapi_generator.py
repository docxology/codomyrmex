"""
OpenAPI Specification Generator for Codomyrmex

This module provides automatic generation of OpenAPI/Swagger specifications
from API definitions, including REST APIs, GraphQL APIs, and versioned endpoints.
"""

import json
import yaml
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

# Import logging
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Import from other modules
from .rest_api import RESTAPI, APIEndpoint, HTTPMethod
from .graphql_api import GraphQLAPI, GraphQLSchema, GraphQLObjectType, GraphQLField
from .api_versioning import APIVersionManager, APIVersion


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


class OpenAPIGenerator:
    """
    Generator for OpenAPI specifications from various API sources.
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

    def _add_rest_endpoint(self, endpoint: APIEndpoint) -> None:
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


# Convenience functions
def generate_openapi_spec(title: str = "Codomyrmex API", version: str = "1.0.0",
                         description: str = "API for Codomyrmex") -> OpenAPIGenerator:
    """
    Create a new OpenAPI generator.

    Args:
        title: API title
        version: API version
        description: API description

    Returns:
        OpenAPIGenerator instance
    """
    return OpenAPIGenerator(title=title, version=version, description=description)


def create_openapi_from_rest_api(api: RESTAPI) -> OpenAPISpecification:
    """
    Create OpenAPI spec from a REST API.

    Args:
        api: REST API instance

    Returns:
        OpenAPI specification
    """
    generator = OpenAPIGenerator(
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
    generator = OpenAPIGenerator(
        title="GraphQL API",
        version="1.0.0",
        description="GraphQL API endpoint"
    )
    generator.add_graphql_api(api)
    return generator.generate_spec()
