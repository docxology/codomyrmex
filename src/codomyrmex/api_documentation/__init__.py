"""
API Documentation Module for Codomyrmex.

The API Documentation module provides comprehensive API documentation generation,
management, and publishing capabilities for the Codomyrmex ecosystem.

Integration:
- Uses `static_analysis` for code introspection and documentation extraction.
- Integrates with `data_visualization` for API usage analytics.
- Works with `logging_monitoring` for API access logging.
- Supports `security_audit` for API security documentation.

Available functions:
- generate_api_docs: Generate comprehensive API documentation
- extract_api_specs: Extract API specifications from code
- publish_documentation: Publish docs to various platforms
- validate_api_docs: Validate API documentation accuracy
- generate_openapi_spec: Generate OpenAPI/Swagger specifications
- create_api_playground: Create interactive API testing environments
- monitor_api_usage: Track and analyze API usage patterns
- generate_api_changelogs: Generate API change documentation

Data structures:
- APIDocumentation: Complete API documentation structure
- APIEndpoint: Individual API endpoint documentation
- APISchema: API data schema definitions
- APIExamples: API usage examples and code samples
- APIChangelog: API change history and versioning
"""

from .doc_generator import (
    APIDocumentation,
    APIDocumentationGenerator,
    APIEndpoint,
    extract_api_specs,
    generate_api_docs,
)
from .openapi_generator import (
    APISchema,
    OpenAPIGenerator,
    generate_openapi_spec,
    validate_openapi_spec,
)

# Note: doc_publisher and usage_analyzer modules are planned for future implementation
# These would provide documentation publishing and API usage analytics capabilities
# Currently, the core documentation generation and OpenAPI spec generation are available

__all__ = [
    # Documentation generation
    "APIDocumentationGenerator",
    "generate_api_docs",
    "extract_api_specs",
    "APIDocumentation",
    "APIEndpoint",
    # OpenAPI/Swagger
    "OpenAPIGenerator",
    "generate_openapi_spec",
    "validate_openapi_spec",
    "APISchema",
    # TODO: Add when implemented
    # 'DocumentationPublisher',
    # 'publish_documentation',
    # 'APIPlayground',
    # 'APIUsageAnalyzer',
    # 'monitor_api_usage',
    # 'generate_api_analytics',
    # 'APIExamples',
]
