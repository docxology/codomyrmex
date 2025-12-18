# API Documentation - API Specification

## Introduction

The API Documentation module provides comprehensive API documentation generation, including OpenAPI/Swagger specifications, interactive documentation, and code-based documentation extraction. It analyzes codebases to automatically generate accurate API documentation.

## Core Functions

### Function: `generate_api_docs()`

- **Description**: Generate comprehensive API documentation from code analysis
- **Parameters/Arguments**:
    - `source_path` (str): Path to source code to document
    - `output_path` (str, optional): Output directory for documentation. Default: `./api_docs`
    - `title` (str, optional): Documentation title. Default: `API Documentation`
    - `version` (str, optional): API version. Default: `1.0.0`
    - `base_url` (str, optional): Base URL for API. Default: `http://localhost:8000`
    - `formats` (list[str], optional): Output formats ('json', 'yaml', 'html', 'markdown'). Default: `['json', 'html']`
- **Returns**:
    - `APIDocumentation`: Complete API documentation object
- **Example**:
```python
from codomyrmex.api_documentation import generate_api_docs

docs = generate_api_docs(
    source_path="./src/api",
    output_path="./docs/api",
    title="My API",
    version="1.0.0",
    formats=['json', 'html', 'markdown']
)
```

### Function: `extract_api_specs()`

- **Description**: Extract API specifications from code files
- **Parameters/Arguments**:
    - `file_path` (str): Path to Python file to analyze
    - `include_private` (bool, optional): Include private methods. Default: `False`
- **Returns**:
    - `list[APIEndpoint]`: List of discovered API endpoints
- **Example**:
```python
from codomyrmex.api_documentation import extract_api_specs

endpoints = extract_api_specs("./src/api/routes.py")
for endpoint in endpoints:
    print(f"{endpoint.method} {endpoint.path}")
```

### Function: `generate_openapi_spec()`

- **Description**: Generate OpenAPI/Swagger 3.0 specification
- **Parameters/Arguments**:
    - `source_path` (str): Path to source code
    - `output_file` (str, optional): Output file path. Default: `openapi.json`
    - `title` (str, optional): API title
    - `version` (str, optional): API version
    - `description` (str, optional): API description
- **Returns**:
    - `dict[str, Any]`: OpenAPI specification dictionary
- **Example**:
```python
from codomyrmex.api_documentation import generate_openapi_spec

spec = generate_openapi_spec(
    source_path="./src/api",
    output_file="openapi.json",
    title="My API",
    version="2.0.0"
)
```

### Function: `validate_openapi_spec()`

- **Description**: Validate OpenAPI specification for correctness
- **Parameters/Arguments**:
    - `spec` (dict[str, Any]): OpenAPI specification to validate
    - `strict` (bool, optional): Strict validation mode. Default: `True`
- **Returns**:
    - `tuple[bool, list[str]]`: (is_valid, list_of_errors)
- **Example**:
```python
from codomyrmex.api_documentation import validate_openapi_spec

is_valid, errors = validate_openapi_spec(spec, strict=True)
if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
```

## Data Models

### Model: `APIEndpoint`

Represents a single API endpoint with complete documentation.

- `path` (str): API endpoint path (e.g., `/api/users/{id}`)
- `method` (str): HTTP method (GET, POST, PUT, DELETE, etc.)
- `summary` (str): Brief endpoint description
- `description` (str): Detailed endpoint documentation
- `parameters` (list[dict]): Query, path, and header parameters
- `request_body` (dict, optional): Request body schema
- `responses` (dict[str, dict]): Response schemas by status code
- `tags` (list[str]): Categorization tags
- `deprecated` (bool): Whether endpoint is deprecated
- `security` (list[dict]): Security requirements

### Model: `APIDocumentation`

Complete API documentation structure.

- `title` (str): API title
- `version` (str): API version
- `description` (str): API description
- `base_url` (str): Base URL for API
- `endpoints` (list[APIEndpoint]): All API endpoints
- `schemas` (dict): Data model schemas
- `security_schemes` (dict): Security/authentication schemes
- `tags` (list[dict]): Available tags and descriptions
- `generated_at` (datetime): Generation timestamp
- `contact_info` (dict[str, str]): Contact information
- `license_info` (dict[str, str]): License information

### Model: `APISchema`

Data schema definition for API models.

- `name` (str): Schema name
- `type` (str): Schema type (object, array, string, etc.)
- `properties` (dict): Object properties
- `required` (list[str]): Required fields
- `description` (str): Schema description
- `example` (Any): Example value

## Classes

### Class: `APIDocumentationGenerator`

Main documentation generation engine.

**Methods**:
- `__init__(source_path: str, config: dict = None)`: Initialize generator
- `analyze_codebase() -> None`: Analyze source code structure
- `extract_endpoints() -> list[APIEndpoint]`: Extract all API endpoints
- `generate_documentation() -> APIDocumentation`: Generate complete documentation
- `export(format: str, output_path: str) -> None`: Export documentation

### Class: `OpenAPIGenerator`

OpenAPI/Swagger specification generator.

**Methods**:
- `__init__(title: str, version: str, description: str = "")`: Initialize generator
- `add_endpoint(endpoint: APIEndpoint) -> None`: Add endpoint to specification
- `add_schema(name: str, schema: dict) -> None`: Add data schema
- `add_security_scheme(name: str, scheme: dict) -> None`: Add security scheme
- `generate_spec() -> dict`: Generate complete OpenAPI specification
- `validate() -> tuple[bool, list[str]]`: Validate specification
- `export_yaml(file_path: str) -> None`: Export as YAML
- `export_json(file_path: str) -> None`: Export as JSON

## Output Formats

### JSON Format
Standard OpenAPI 3.0 JSON format compatible with Swagger UI and other tools.

### YAML Format
OpenAPI 3.0 YAML format for human-readable specifications.

### HTML Format
Interactive HTML documentation with syntax highlighting and examples.

### Markdown Format
Markdown documentation suitable for GitHub and documentation sites.

## Integration

### With Static Analysis
Uses static analysis to extract function signatures, docstrings, and type hints.

### With Documentation Module
Provides API documentation for inclusion in Docusaurus sites.

### With Build Synthesis
Generates API documentation as part of build artifacts.

## Versioning

API documentation follows semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking API changes
- MINOR: New endpoints or features
- PATCH: Bug fixes and documentation updates

## Security Considerations

- Excludes private/internal endpoints from public documentation
- Redacts sensitive information from examples
- Validates all generated specifications for security issues
- Supports API key, OAuth 2.0, and custom authentication documentation

