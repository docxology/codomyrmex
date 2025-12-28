# Codomyrmex Agents — src/codomyrmex/api_documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core Service Layer module providing API documentation generation, OpenAPI specification creation, and API documentation management capabilities for the Codomyrmex platform. This module enables automated generation of API documentation from code analysis and provides tools for API specification management.

The api_documentation module serves as the API knowledge layer, ensuring clear, accurate, and accessible API documentation across all platform services.

## Module Overview

### Key Capabilities
- **API Documentation Generation**: Automated extraction and formatting of API documentation
- **OpenAPI Specification**: Standards-compliant API specification generation
- **API Validation**: Documentation accuracy and completeness validation
- **Multi-format Output**: Support for various documentation formats and platforms

### Key Features
- Code introspection for automatic API discovery
- OpenAPI/Swagger specification generation
- Interactive API documentation with examples
- API change tracking and versioning
- Integration with existing code analysis tools

## Function Signatures

### API Documentation Generation Functions

```python
def generate_api_docs(
    title: str,
    version: str,
    source_paths: Optional[list[str]] = None,
    base_url: str = "http://localhost:8000",
) -> APIDocumentation
```

Generate API documentation from source code.

**Parameters:**
- `title` (str): API documentation title
- `version` (str): API version string
- `source_paths` (Optional[list[str]]): Paths to scan for API endpoints. If None, uses defaults
- `base_url` (str): Base URL for the API. Defaults to "http://localhost:8000"

**Returns:** `APIDocumentation` - Complete API documentation object

```python
def extract_api_specs(source_path: str) -> list[APIEndpoint]
```

Extract API specifications from source code files.

**Parameters:**
- `source_path` (str): Path to source code to analyze

**Returns:** `list[APIEndpoint]` - List of discovered API endpoints with specifications

### OpenAPI Specification Functions

```python
def generate_openapi_spec(
    title: str,
    version: str,
    endpoints: list[Any],
    base_url: str = "http://localhost:8000",
) -> dict[str, Any]
```

Generate OpenAPI/Swagger specification from API endpoints.

**Parameters:**
- `title` (str): API specification title
- `version` (str): API version string
- `endpoints` (list[Any]): List of API endpoints to include in specification
- `base_url` (str): Base API URL. Defaults to "http://localhost:8000"

**Returns:** `dict[str, Any]` - OpenAPI specification dictionary

```python
def validate_openapi_spec(spec: dict[str, Any]) -> list[str]
```

Validate an OpenAPI specification for correctness and completeness.

**Parameters:**
- `spec` (dict[str, Any]): OpenAPI specification to validate

**Returns:** `list[str]` - List of validation errors. Empty list means specification is valid

## Data Structures

### APIDocumentation
```python
class APIDocumentation:
    title: str
    version: str
    base_url: str
    endpoints: list[APIEndpoint]
    schemas: dict[str, APISchema]
    examples: list[APIExamples]
    changelog: APIChangelog

    def to_dict(self) -> dict[str, Any]
    def to_markdown(self) -> str
    def to_html(self) -> str
    def validate(self) -> list[str]
```

Complete API documentation structure containing all API information.

### APIEndpoint
```python
class APIEndpoint:
    path: str
    method: str
    summary: str
    description: str
    parameters: list[dict[str, Any]]
    request_body: Optional[dict[str, Any]]
    responses: dict[str, dict[str, Any]]
    tags: list[str]
    security: Optional[list[dict[str, Any]]]

    def to_openapi(self) -> dict[str, Any]
    def validate(self) -> list[str]
```

Individual API endpoint documentation with complete specification.

### APISchema
```python
class APISchema:
    name: str
    type: str
    properties: dict[str, dict[str, Any]]
    required: list[str]
    example: Any

    def to_openapi(self) -> dict[str, Any]
    def validate(self) -> list[str]
```

API data schema definition for request/response bodies.

### APIExamples
```python
class APIExamples:
    endpoint: str
    method: str
    title: str
    description: str
    request: dict[str, Any]
    response: dict[str, Any]

    def to_dict(self) -> dict[str, Any]
    def to_code_sample(self, language: str = "python") -> str
```

API usage examples and code samples.

### APIChangelog
```python
class APIChangelog:
    version: str
    date: str
    changes: list[dict[str, str]]
    breaking_changes: list[str]

    def to_markdown(self) -> str
    def add_change(self, change_type: str, description: str) -> None
```

API change history and version tracking.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `doc_generator.py` – API documentation generation from code analysis
- `openapi_generator.py` – OpenAPI/Swagger specification creation

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `SECURITY.md` – Security considerations for API documentation

## Operating Contracts

### Universal API Documentation Protocols

All API documentation within the Codomyrmex platform must:

1. **Accuracy** - Documentation matches actual API behavior and specifications
2. **Completeness** - All API endpoints, parameters, and responses are documented
3. **Consistency** - Documentation follows consistent patterns and formats
4. **Accessibility** - Documentation is available in appropriate formats for different audiences
5. **Maintainability** - Documentation stays synchronized with API changes

### Module-Specific Guidelines

#### API Documentation Generation
- Automatically extract documentation from code annotations and comments
- Support multiple programming languages and frameworks
- Generate documentation in multiple formats (HTML, Markdown, JSON)
- Include code examples and usage patterns

#### OpenAPI Specification
- Generate standards-compliant OpenAPI specifications
- Support OpenAPI versions 3.0 and 3.1
- Include schema definitions
- Validate specifications against OpenAPI schema

#### Documentation Validation
- Validate documentation completeness and accuracy
- Check for broken links and references
- Ensure consistent formatting and terminology
- Verify examples work with actual API

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations

### Related Modules
- **static_analysis**: Code analysis for API discovery
- **data_visualization**: API usage analytics and reporting
- **security_audit**: API security documentation
- **documentation**: API documentation publishing

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **Code Analysis** - Use static_analysis for API endpoint discovery
2. **Documentation Publishing** - Integrate with documentation module for website publishing
3. **Security Integration** - Coordinate with security_audit for API security docs
4. **Usage Analytics** - Work with data_visualization for API usage reporting

### Quality Gates

Before API documentation changes are accepted:

1. **API Accuracy** - Generated documentation matches actual API behavior
2. **Specification Validity** - OpenAPI specifications pass validation
3. **Completeness Check** - All API endpoints are documented
4. **Example Validation** - Code examples work with actual APIs
5. **Format Compliance** - Documentation follows established standards

## Version History

- **v0.1.0** (December 2025) - Initial API documentation system with OpenAPI generation and automated documentation extraction
