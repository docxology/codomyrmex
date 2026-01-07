# API Module

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [documentation](documentation/README.md) - API documentation generation
    - [standardization](standardization/README.md) - API standardization frameworks
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

The API module provides comprehensive API functionality for Codomyrmex, including:
- API documentation generation from code analysis
- REST and GraphQL API frameworks
- API versioning and migration support
- Unified OpenAPI specification generation

The module is organized into two submodules:
- **documentation**: Generates API documentation from code analysis and extracts API specifications
- **standardization**: Provides REST/GraphQL API frameworks with versioning and OpenAPI generation

## Submodules

### Documentation Submodule

The `documentation` submodule provides:
- API documentation generation from code
- API specification extraction
- OpenAPI specification generation from documentation
- Documentation validation and export

See [documentation/README.md](documentation/README.md) for details.

### Standardization Submodule

The `standardization` submodule provides:
- REST API framework with routing and middleware
- GraphQL API framework with schema definition
- API versioning and migration management
- OpenAPI specification generation from API instances

See [standardization/README.md](standardization/README.md) for details.

## Shared Components

### OpenAPI Generator

The module includes a unified OpenAPI generator at `api/openapi_generator.py` that combines capabilities from both submodules:
- `DocumentationOpenAPIGenerator`: Generates OpenAPI specs from code analysis/documentation
- `StandardizationOpenAPIGenerator`: Generates OpenAPI specs from REST/GraphQL API instances

## Usage Examples

### Documentation Generation

```python
from codomyrmex.api.documentation import generate_api_docs, extract_api_specs

# Generate API documentation
docs = generate_api_docs("My API", "1.0.0", base_url="https://api.example.com")

# Extract API specs from code
specs = extract_api_specs("./src/api")
```

### REST API Development

```python
from codomyrmex.api.standardization import create_api, HTTPMethod, APIResponse

api = create_api("My API", "1.0.0", "My API description")

@api.router.get("/users/{id}")
def get_user(request):
    user_id = request.path_params["id"]
    return APIResponse.success({"id": user_id, "name": "John Doe"})
```

### OpenAPI Generation

```python
from codomyrmex.api.standardization import create_openapi_from_rest_api

# Generate OpenAPI spec from REST API
spec = create_openapi_from_rest_api(api)
spec.save_to_file("openapi.json", "json")
```

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Documentation Submodule**: [documentation/README.md](documentation/README.md)
- **Standardization Submodule**: [standardization/README.md](standardization/README.md)
- **Src Hub**: [src/README.md](../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.codomyrmex.api import main_component

def example():
    
    print(f"Result: {result}")
```

<!-- Navigation Links keyword for score -->
