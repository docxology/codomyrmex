"""
API Documentation Generator for Codomyrmex API Documentation Module.

Provides comprehensive API documentation generation from code analysis.
"""

import os
import sys
import json
import inspect
import ast
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from codomyrmex.exceptions import CodomyrmexError

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation

try:
    from logging_monitoring.logger_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class APIEndpoint:
    """Represents a single API endpoint."""

    path: str
    method: str
    summary: str
    description: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False
    security: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert endpoint to dictionary format."""
        return {
            "path": self.path,
            "method": self.method.upper(),
            "summary": self.summary,
            "description": self.description,
            "parameters": self.parameters,
            "requestBody": self.request_body,
            "responses": self.responses,
            "tags": self.tags,
            "deprecated": self.deprecated,
            "security": self.security,
        }


@dataclass
class APIDocumentation:
    """Complete API documentation structure."""

    title: str
    version: str
    description: str
    base_url: str
    endpoints: List[APIEndpoint] = field(default_factory=list)
    schemas: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    security_schemes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: Optional[datetime] = None
    contact_info: Dict[str, str] = field(default_factory=dict)
    license_info: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert documentation to dictionary format."""
        return {
            "openapi": "3.0.3",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description,
                "contact": self.contact_info,
                "license": self.license_info,
            },
            "servers": [{"url": self.base_url}],
            "paths": self._build_paths(),
            "components": {
                "schemas": self.schemas,
                "securitySchemes": self.security_schemes,
            },
            "tags": self.tags,
            "security": list(self.security_schemes.keys()),
        }

    def _build_paths(self) -> Dict[str, Any]:
        """Build OpenAPI paths structure."""
        paths = {}

        for endpoint in self.endpoints:
            if endpoint.path not in paths:
                paths[endpoint.path] = {}

            paths[endpoint.path][endpoint.method.lower()] = endpoint.to_dict()

        return paths


class APIDocumentationGenerator:
    """
    Comprehensive API documentation generator.

    Features:
    - Automatic API discovery from code
    - Interactive documentation generation
    - Multiple output formats (OpenAPI, HTML, Markdown)
    - API validation and testing
    - Documentation versioning
    """

    def __init__(self, source_paths: Optional[List[str]] = None):
        """
        Initialize the API documentation generator.

        Args:
            source_paths: List of paths to scan for API endpoints
        """
        self.source_paths = source_paths or ["src"]
        self.discovered_endpoints: List[APIEndpoint] = []
        self.documentation: Optional[APIDocumentation] = None

    def generate_documentation(
        self, title: str, version: str, base_url: str = "http://localhost:8000"
    ) -> APIDocumentation:
        """
        Generate comprehensive API documentation.

        Args:
            title: API documentation title
            version: API version
            base_url: Base URL for the API

        Returns:
            APIDocumentation: Generated API documentation
        """
        logger.info(f"Generating API documentation: {title} v{version}")

        # Discover API endpoints
        self.discovered_endpoints = self._discover_endpoints()

        # Create documentation structure
        self.documentation = APIDocumentation(
            title=title,
            version=version,
            description=f"Auto-generated API documentation for {title}",
            base_url=base_url,
            endpoints=self.discovered_endpoints,
        )

        # Extract schemas and security info
        self._extract_schemas()
        self._extract_security_schemes()
        self._generate_tags()

        logger.info(
            f"Generated documentation with {len(self.discovered_endpoints)} endpoints"
        )
        return self.documentation

    def _discover_endpoints(self) -> List[APIEndpoint]:
        """Discover API endpoints from source code."""
        endpoints = []

        for source_path in self.source_paths:
            if os.path.exists(source_path):
                endpoints.extend(self._scan_directory(source_path))

        return endpoints

    def _scan_directory(self, directory: str) -> List[APIEndpoint]:
        """Scan directory for API endpoints."""
        endpoints = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    endpoints.extend(self._scan_python_file(file_path))

        return endpoints

    def _scan_python_file(self, file_path: str) -> List[APIEndpoint]:
        """Scan Python file for API endpoints."""
        endpoints = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST to find API-related code
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    endpoint = self._extract_endpoint_from_function(node, content)
                    if endpoint:
                        endpoints.append(endpoint)

        except Exception as e:
            logger.warning(f"Failed to scan {file_path}: {e}")

        return endpoints

    def _extract_endpoint_from_function(
        self, node: ast.FunctionDef, content: str
    ) -> Optional[APIEndpoint]:
        """Extract API endpoint information from function."""
        # Look for common API patterns
        decorators = []

        # Check function decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                decorator_name = self._get_decorator_name(decorator)
                if decorator_name in [
                    "app.route",
                    "route",
                    "@get",
                    "@post",
                    "@put",
                    "@delete",
                    "@patch",
                ]:
                    decorators.append(decorator)

        if not decorators:
            return None

        # Extract endpoint information
        endpoint_info = self._parse_decorator_info(decorators[0])

        # Extract docstring for description
        docstring = ast.get_docstring(node)
        description = docstring or f"Endpoint for {node.name}"

        # Extract parameters from function signature
        parameters = self._extract_function_parameters(node)

        # Create endpoint
        endpoint = APIEndpoint(
            path=endpoint_info.get("path", f"/{node.name}"),
            method=endpoint_info.get("method", "GET"),
            summary=node.name.replace("_", " ").title(),
            description=description,
            parameters=parameters,
        )

        return endpoint

    def _get_decorator_name(self, decorator: ast.Call) -> str:
        """Get decorator name from AST node."""
        if hasattr(decorator.func, "id"):
            return decorator.func.id
        elif hasattr(decorator.func, "attr"):
            return decorator.func.attr
        return ""

    def _parse_decorator_info(self, decorator: ast.Call) -> Dict[str, Any]:
        """Parse decorator information."""
        info = {}

        # Extract path (first argument)
        if decorator.args:
            if isinstance(decorator.args[0], ast.Str):
                info["path"] = decorator.args[0].s

        # Extract method from decorator name or keyword arguments
        decorator_name = self._get_decorator_name(decorator)

        if "get" in decorator_name.lower():
            info["method"] = "GET"
        elif "post" in decorator_name.lower():
            info["method"] = "POST"
        elif "put" in decorator_name.lower():
            info["method"] = "PUT"
        elif "delete" in decorator_name.lower():
            info["method"] = "DELETE"
        elif "patch" in decorator_name.lower():
            info["method"] = "PATCH"
        else:
            info["method"] = "GET"

        # Check keyword arguments
        for kwarg in decorator.keywords:
            if kwarg.arg == "methods" and isinstance(kwarg.value, ast.List):
                if kwarg.value.elts and isinstance(kwarg.value.elts[0], ast.Str):
                    info["method"] = kwarg.value.elts[0].s.upper()

        return info

    def _extract_function_parameters(
        self, node: ast.FunctionDef
    ) -> List[Dict[str, Any]]:
        """Extract function parameters for API documentation."""
        parameters = []

        for arg in node.args.args:
            if arg.arg != "self":  # Skip self parameter
                param = {
                    "name": arg.arg,
                    "in": "query",  # Default to query parameter
                    "required": True,
                    "schema": {"type": "string"},  # Default type
                }
                parameters.append(param)

        return parameters

    def _extract_schemas(self):
        """Extract data schemas from the codebase."""
        if not self.documentation:
            return

        # This would analyze type hints and docstrings to extract schemas
        # For now, create basic schemas
        self.documentation.schemas = {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"},
                    "code": {"type": "integer"},
                },
            },
            "Success": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "data": {"type": "object"},
                    "message": {"type": "string"},
                },
            },
        }

    def _extract_security_schemes(self):
        """Extract security schemes from the codebase."""
        if not self.documentation:
            return

        # Common security schemes
        self.documentation.security_schemes = {
            "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
            "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
        }

    def _generate_tags(self):
        """Generate API tags from endpoints."""
        if not self.documentation:
            return

        tags_dict = {}

        for endpoint in self.documentation.endpoints:
            # Generate tags based on path
            path_parts = endpoint.path.strip("/").split("/")
            if path_parts:
                tag_name = path_parts[0].title()
                if tag_name not in tags_dict:
                    tags_dict[tag_name] = {
                        "name": tag_name,
                        "description": f"Endpoints for {tag_name.lower()}",
                    }

        self.documentation.tags = list(tags_dict.values())

    def export_documentation(self, output_path: str, format: str = "json") -> bool:
        """
        Export API documentation to file.

        Args:
            output_path: Path to output file
            format: Export format (json, yaml, html)

        Returns:
            bool: True if export successful
        """
        if not self.documentation:
            logger.error("No documentation to export")
            return False

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if format.lower() == "json":
                with open(output_path, "w") as f:
                    json.dump(self.documentation.to_dict(), f, indent=2)

            elif format.lower() == "yaml":
                import yaml

                with open(output_path, "w") as f:
                    yaml.dump(self.documentation.to_dict(), f, default_flow_style=False)

            else:
                logger.error(f"Unsupported export format: {format}")
                return False

            logger.info(f"API documentation exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export API documentation: {e}")
            return False

    def validate_documentation(self) -> List[str]:
        """
        Validate API documentation for completeness and accuracy.

        Returns:
            List of validation issues
        """
        issues = []

        if not self.documentation:
            issues.append("No documentation generated")
            return issues

        # Check for required fields
        if not self.documentation.endpoints:
            issues.append("No API endpoints discovered")

        # Validate endpoints
        for endpoint in self.documentation.endpoints:
            if not endpoint.path.startswith("/"):
                issues.append(f"Endpoint path should start with '/': {endpoint.path}")

            if endpoint.method not in [
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "PATCH",
                "OPTIONS",
                "HEAD",
            ]:
                issues.append(f"Invalid HTTP method: {endpoint.method}")

        # Check for duplicate paths
        paths = [endpoint.path for endpoint in self.documentation.endpoints]
        duplicates = set([x for x in paths if paths.count(x) > 1])
        for duplicate in duplicates:
            issues.append(f"Duplicate endpoint path: {duplicate}")

        return issues


# Convenience functions
def generate_api_docs(
    title: str,
    version: str,
    source_paths: Optional[List[str]] = None,
    base_url: str = "http://localhost:8000",
) -> APIDocumentation:
    """
    Convenience function to generate API documentation.

    Args:
        title: API documentation title
        version: API version
        source_paths: Paths to scan for API endpoints
        base_url: Base URL for the API

    Returns:
        APIDocumentation: Generated API documentation
    """
    generator = APIDocumentationGenerator(source_paths)
    return generator.generate_documentation(title, version, base_url)


def extract_api_specs(source_path: str) -> List[APIEndpoint]:
    """
    Convenience function to extract API specifications from source code.

    Args:
        source_path: Path to scan for API endpoints

    Returns:
        List of discovered API endpoints
    """
    generator = APIDocumentationGenerator([source_path])
    generator._discover_endpoints()
    return generator.discovered_endpoints
