# api/documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

API documentation generation, management, and publishing capabilities for the Codomyrmex ecosystem. Uses `static_analysis` for code introspection, integrates with `data_visualization` for API usage analytics, and works with `logging_monitoring` for access logging. Generates OpenAPI/Swagger specifications and structured API documentation from source code.

## Key Exports

### Documentation Generation

- **`APIDocumentationGenerator`** -- Main documentation generator class
- **`generate_api_docs()`** -- Generate API documentation from source
- **`extract_api_specs()`** -- Extract API specifications from code

### Data Structures

- **`APIDocumentation`** -- Complete API documentation structure
- **`APIEndpoint`** -- Individual API endpoint documentation

### OpenAPI/Swagger (from parent module)

- **`OpenAPIGenerator`** -- OpenAPI specification generator (aliased from `DocumentationOpenAPIGenerator`)
- **`generate_openapi_spec()`** -- Generate OpenAPI/Swagger specifications
- **`validate_openapi_spec()`** -- Validate OpenAPI specification accuracy
- **`APISchema`** -- API data schema definitions

### Planned (not yet implemented)

- `DocumentationPublisher` -- Documentation publishing to various platforms
- `APIPlayground` -- Interactive API testing environments
- `APIUsageAnalyzer` -- API usage pattern tracking and analytics

## Directory Contents

- `__init__.py` - Package init; re-exports from `doc_generator` and parent `openapi_generator`
- `doc_generator.py` - Core documentation generation logic
- `API_SPECIFICATION.md` - API specification for this module
- `USAGE_EXAMPLES.md` - Usage examples and code samples
- `SECURITY.md` - API security documentation
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [api](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
