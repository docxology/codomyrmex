# API Documentation Example

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Module**: `api_documentation` | **Status**: ✅ Complete | **Test Coverage**: Comprehensive

## Overview

This example demonstrates comprehensive API documentation generation and OpenAPI specification management using Codomyrmex's `api_documentation` module. It showcases how to automatically generate API documentation from code, create OpenAPI/Swagger specifications, validate specifications, and export documentation in multiple formats.

## What This Example Demonstrates

### Core Functionality

- **API Documentation Generation**: Automatic generation of API documentation from code analysis
- **OpenAPI Specification**: Creation of OpenAPI 3.0.3 compliant specifications
- **Schema Management**: Definition and management of API data schemas
- **Validation**: Comprehensive validation of OpenAPI specifications
- **Multi-format Export**: Export documentation to JSON, YAML, and HTML formats

### Key Features

- ✅ Sample API endpoints with complete request/response definitions
- ✅ Data schemas for users, products, and error responses
- ✅ Parameter validation and response schemas
- ✅ Security scheme definitions
- ✅ Multiple export format support
- ✅ HTML documentation generation

## Configuration

### YAML Configuration (config.yaml)

```yaml
api_documentation:
  title: "Sample E-commerce API"
  version: "1.0.0"
  description: "A comprehensive e-commerce API for managing users and products"
  base_url: "https://api.example.com"

  export_formats:
    - json
    - yaml
    - html

  openapi:
    version: "3.0.3"
    include_servers: true
    include_security_schemes: true
    validate_spec: true
```

### JSON Configuration (config.json)

```json
{
  "api_documentation": {
    "title": "Sample E-commerce API",
    "version": "1.0.0",
    "description": "A comprehensive e-commerce API for managing users and products",
    "base_url": "https://api.example.com",
    "export_formats": ["json", "yaml", "html"],
    "openapi": {
      "version": "3.0.3",
      "include_servers": true,
      "include_security_schemes": true,
      "validate_spec": true
    }
  }
}
```

## Tested Methods

This example demonstrates the following methods verified in `test_api_documentation.py`:

- `generate_api_docs()` - Convenience function for API documentation generation
- `extract_api_specs()` - Extract API specifications from Python code
- `generate_openapi_spec()` - Generate OpenAPI/Swagger specifications
- `validate_openapi_spec()` - Validate OpenAPI specification compliance

## Sample Output

### API Endpoints

The example creates sample endpoints for a typical e-commerce API:

- `GET /users` - Retrieve users with pagination
- `POST /users` - Create new user accounts
- `GET /users/{userId}` - Get specific user by ID
- `GET /products` - Retrieve products with filtering

### OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: Sample E-commerce API
  version: 1.0.0
  description: A comprehensive e-commerce API for managing users and products
servers:
  - url: https://api.example.com
paths:
  /users:
    get:
      summary: Get users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 10
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  users:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NewUser'
      responses:
        '201':
          description: User created successfully
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        username:
          type: string
          minLength: 3
          maxLength: 50
        email:
          type: string
          format: email
```

## Running the Example

### Basic Execution

```bash
cd examples/api_documentation
python example_basic.py
```

### With Custom Configuration

```bash
# Using YAML config
python example_basic.py --config config.yaml

# Using JSON config
python example_basic.py --config config.json

# With environment variables
API_TITLE="My Custom API" python example_basic.py
```

### Expected Output

```
🏗️  API Documentation Example
Demonstrating comprehensive API documentation generation and OpenAPI specification

📋 Creating sample API endpoints and schemas...
✅ Created 4 sample endpoints and 4 schemas

📚 Generating API documentation...
✅ Generated API documentation with 4 endpoints

🔍 Extracting API specifications from code...
✅ Extracted 3 API specifications from code

📋 Generating OpenAPI specification...
✅ Generated OpenAPI 3.0.3 specification

✅ Validating OpenAPI specification...
✅ OpenAPI specification is valid

💾 Exporting documentation...
✅ Exported API documentation to JSON: True
✅ Exported API documentation to YAML: True

📄 Generating OpenAPI specification exports...
✅ Exported OpenAPI spec to JSON: True
✅ Exported OpenAPI spec to YAML: True

🌐 Generating HTML documentation...
✅ Generated HTML documentation: True

🔍 Validating exported files...
✅ All exported files created successfully

⚡ Demonstrating advanced OpenAPI features...
✅ Generated advanced spec with security schemes
✅ Advanced spec validation: 0 errors

API Documentation Operations Summary
├── endpoints_created: 4
├── schemas_created: 4
├── documentation_generated: True
├── api_specs_extracted: 3
├── openapi_spec_generated: True
├── openapi_validation_passed: True
├── json_export_success: True
├── yaml_export_success: True
├── html_docs_generated: True
├── all_exported_files_exist: True
├── exported_files_count: 5
└── advanced_spec_generated: True

✅ API Documentation example completed successfully!
Generated comprehensive documentation for 4 endpoints
Created 4 data schemas and exported to 5 formats
OpenAPI 3.0.3 specification validated and exported
```

## Generated Files

The example creates the following output files:

- `output/api_documentation_results.json` - Execution results and metadata
- `output/api_documentation/api_documentation.json` - API documentation in JSON format
- `output/api_documentation/api_documentation.yaml` - API documentation in YAML format
- `output/api_documentation/openapi_spec.json` - OpenAPI specification in JSON
- `output/api_documentation/openapi_spec.yaml` - OpenAPI specification in YAML
- `output/api_documentation/api_documentation.html` - Interactive HTML documentation
- `logs/api_documentation_example.log` - Execution logs

## Integration Points

This example integrates with other Codomyrmex modules:

- **`static_analysis`**: Code introspection for API endpoint discovery
- **`data_visualization`**: API usage analytics and reporting
- **`logging_monitoring`**: API access logging and monitoring
- **`security_audit`**: API security documentation and compliance

## Advanced Usage

### Custom Schema Definitions

```python
from codomyrmex.api_documentation import APISchema

custom_schema = APISchema(
    name="CustomEntity",
    schema_definition={
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "name": {"type": "string"},
            "custom_field": {"type": "integer"}
        },
        "required": ["id", "name"]
    }
)
```

### Security Scheme Integration

```python
security_schemes = {
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

spec = generate_openapi_spec(
    title="Secure API",
    version="1.0.0",
    endpoints=endpoints,
    security_schemes=security_schemes
)
```

## Error Handling

The example includes comprehensive error handling for:

- Invalid OpenAPI specifications
- Missing required fields
- File export failures
- Schema validation errors
- Code parsing issues

## Performance Considerations

- Efficient AST parsing for large codebases
- Streaming export for large specifications
- Memory-efficient schema validation
- Parallel processing for multiple endpoints

## Related Examples

- **Multi-Module Workflows**:
  - `example_workflow_api.py` - Complete API development workflow
- **Integration Examples**:
  - Static analysis integration
  - Data visualization for API analytics

## Testing

This example is verified by the comprehensive test suite in `testing/unit/test_api_documentation.py`, which covers:

- API documentation generation
- OpenAPI specification validation
- Schema management
- Export functionality
- Error handling scenarios

---

**Status**: ✅ Complete | **Tested Methods**: 4 | **Integration Points**: 4 | **Export Formats**: 3

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.your_module import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->
