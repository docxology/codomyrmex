"""
Unified OpenAPI Specification Generator for Codomyrmex API Module.

This module provides comprehensive OpenAPI/Swagger specification generation
from multiple sources:
- Code analysis and documentation extraction
- REST API instances
- GraphQL API instances
- Versioned endpoints

The generator classes have been split into dedicated modules:
- openapi_documentation_generator.py: DocumentationOpenAPIGenerator
- openapi_standardization_generator.py: StandardizationOpenAPIGenerator

This module retains the shared data classes (APISchema, OpenAPISpecification)
and convenience functions, and re-exports the generator classes for backward
compatibility.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.config_management.defaults import DEFAULT_API_BASE_URL

try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Import from standardization submodule for type annotations in convenience functions
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .standardization.graphql_api import GraphQLAPI
    from .standardization.rest_api import RESTAPI
else:
    try:
        from codomyrmex.api.standardization.graphql_api import GraphQLAPI
        from codomyrmex.api.standardization.rest_api import RESTAPI
    except (ImportError, AttributeError):
        RESTAPI = None
        GraphQLAPI = None


@dataclass
class APISchema:
    """API schema definition for documentation generation."""

    name: str
    schema_type: str
    properties: dict[str, Any] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)
    example: dict[str, Any] | None = None

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
    spec: dict[str, Any] = field(default_factory=dict)
    version: str = "3.0.3"

    def to_dict(self) -> dict[str, Any]:
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


# Re-export generator classes from their dedicated modules
from .openapi_documentation_generator import DocumentationOpenAPIGenerator  # noqa: E402, I001
from .openapi_standardization_generator import StandardizationOpenAPIGenerator  # noqa: E402, I001


# Convenience functions for documentation module
def generate_openapi_spec(
    title: str,
    version: str,
    endpoints: list[Any],
    base_url: str = "",
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
    base_url = base_url or os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL)
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
    global RESTAPI
    if RESTAPI is None:
        try:
            from codomyrmex.api.standardization.rest_api import RESTAPI as _RESTAPI
            RESTAPI = _RESTAPI
        except ImportError:
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
