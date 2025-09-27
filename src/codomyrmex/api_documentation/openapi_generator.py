"""
OpenAPI/Swagger Generator for Codomyrmex API Documentation Module.

Provides OpenAPI 3.0 specification generation and validation.
"""

import os
import sys
import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from logging_monitoring.logger_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class APISchema:
    """API schema definition."""

    name: str
    schema_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    example: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to OpenAPI format."""
        schema = {"type": self.schema_type, "properties": self.properties}

        if self.required:
            schema["required"] = self.required

        if self.example:
            schema["example"] = self.example

        return schema


class OpenAPIGenerator:
    """
    OpenAPI 3.0 specification generator and validator.

    Features:
    - Automatic OpenAPI spec generation
    - Specification validation
    - Schema inference
    - Interactive API documentation
    - Multiple output formats
    """

    def __init__(self):
        """Initialize the OpenAPI generator."""
        self.openapi_version = "3.0.3"

    def generate_spec(
        self,
        title: str,
        version: str,
        endpoints: List[Any],
        base_url: str = "http://localhost:8000",
    ) -> Dict[str, Any]:
        """
        Generate OpenAPI 3.0 specification.

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

    def _get_default_schemas(self) -> Dict[str, Any]:
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

    def _get_default_security_schemes(self) -> Dict[str, Any]:
        """Get default security schemes."""
        return {
            "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
            "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
            "BasicAuth": {"type": "http", "scheme": "basic"},
        }

    def validate_spec(self, spec: Dict[str, Any]) -> List[str]:
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
        self, spec: Dict[str, Any], output_path: str, format: str = "json"
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

    def generate_html_docs(self, spec: Dict[str, Any], output_path: str) -> bool:
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

    def _generate_html_content(self, spec: Dict[str, Any]) -> str:
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


# Convenience functions
def generate_openapi_spec(
    title: str,
    version: str,
    endpoints: List[Any],
    base_url: str = "http://localhost:8000",
) -> Dict[str, Any]:
    """
    Convenience function to generate OpenAPI specification.

    Args:
        title: API title
        version: API version
        endpoints: List of API endpoints
        base_url: Base API URL

    Returns:
        Dict containing OpenAPI specification
    """
    generator = OpenAPIGenerator()
    return generator.generate_spec(title, version, endpoints, base_url)


def validate_openapi_spec(spec: Dict[str, Any]) -> List[str]:
    """
    Convenience function to validate OpenAPI specification.

    Args:
        spec: OpenAPI specification dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    generator = OpenAPIGenerator()
    return generator.validate_spec(spec)
